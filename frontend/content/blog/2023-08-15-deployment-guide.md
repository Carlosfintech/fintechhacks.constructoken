---
title: Deployment guide for production
description: "Deploying to a VPS and preparing for production."
author: Gavin Chait
publishedAt: 2023-08-15
categories: [vps, production]
---

# Deployment guide for production

---

## Contents

- [Update deployment](#update-deployment)
- [Preparation](#preparation)
   - [Server resource requirements](#server-resource-requirements)
   - [Committing to GitHub](#committing-to-github)
   - [Configure your DNS](#configure-your-DNS)
   - [Install Docker on your server](#install-docker-on-your-server)
   - [Clone your repository](#clone-your-repository)
- [Configure Traefik](#configure-traefik)
   - [Set up Traefik public network](#set-up-traefik-public-network)
   - [Export Traefik environment variables](#export-traefik-environment-variables)
   - [Start the Traefik Docker Compose](#start-the-traefik-docker-compose)
- [Deploy your project](#deploy-your-project)
   - [Set environment variables](#set-environment-variables)
   - [Ensure `frontend` `Docker` dependencies](#ensure-frontend-docker-dependencies)
   - [Deploy with Docker Compose](#deploy-with-docker-compose)
- [Production URLs](#production-urls)

There are [easier ways to run a blog](https://github.com/myles/awesome-static-generators). You will find the resource requirements for this stack quite substantive. It needs 4Gb of RAM just to complete the `docker compose` build process. This really is if you intend to run some complex web service and need all the architecture.

## Update deployment

This section is a summary which is how you run this from the command line on any updates to your repo. Note, this can be turned into a continuous deployment process as well.

```console
cd /<service directory>
git pull
docker compose -f docker-compose.yml up -d --force-recreate --build
```

Then, you may need to do this:

```console
service docker restart
```

And you could also `prune` to remove builds and free up space:

```console
docker system prune -f
```

Finally, review logs:

```console
docker container ls
docker logs <container name>
```

If a container keeps dying, then do it this way:

```console
docker ps -a
docker logs <container name>
```

## Preparation

### Server resource requirements

These are the minimum hardware requirements to build the base template project. You may find that your particular implementation requires more.

| Component | Min.   |
| --------- | ------ |
| Memory    | 4 Gb   |
| CPU       | 1 core |
| Storage   | 25 Gb  |

This guide deploys to Ubuntu Server 24.04 LTS (Noble Numbat) on a VPS according to these minimum resource requirements.

Ensure you add your SSH encryption keys on launch so that your server can be secure from the beginning.

Deploy on whatever service provider you prefer.

### Committing to GitHub

Prepare your code and resources for your first commit. There are two files which must **not** be committed unless you're quite positive your data will never leak.

- `/.env`
- `/frontend/.env`

These files will also need to be customised for production deployment. Make alternative arrangements for these files. Don't trust `.gitignore` to save you.

### Configure your DNS

Get your settings and redirects at your registrar, and then set up the various DNS records at your registrar, pointing at the IP address for the VPS you set up.

Configure a wildcard subdomain for your domain, e.g. `*.fastapi-project.example.com`. This lets `traefik` manage the multiple subdomains for different your services. This will be useful for accessing different components, like `fastapi-project.example.com`, `api.fastapi-project.example.com`, `traefik.fastapi-project.example.com`, `adminer.fastapi-project.example.com`, etc. And also for `staging`, like `dashboard.staging.fastapi-project.example.com`, `adminer.staging.fastapi-project.example.com`, etc.

For reference: 
- [Link Namecheap domain to DigitalOcean](https://www.namecheap.com/support/knowledgebase/article.aspx/10375/2208/how-do-i-link-a-domain-to-my-digitalocean-account/)
- [Manage DNS records at DigitalOcean](https://docs.digitalocean.com/products/networking/dns/how-to/manage-records/)

If you want a [European alternative to DigitalOcean](https://european-alternatives.eu/alternative-to/digitalocean). [OVH](https://www.ovhcloud.com/en/vps/) has a $4.70/month which happily meets these criteria, and includes DDoS protection.

Now you should be able to login to your server and begin deployment.

### Install Docker on your server

Update your server, and install all required packages:

```shell
# Install the latest updates
apt-get update
apt-get upgrade -y
```

Then:

```shell
# Download Docker 
curl -fsSL get.docker.com -o get-docker.sh
# Install Docker using the stable channel (instead of the default "edge") 
CHANNEL=stable sh get-docker.sh
# Remove Docker install script 
rm get-docker.sh
```

### Clone your repository

The basic approach is to clone from GitHub then set up the appropriate `.env` files and any custom `conf` files called from `docker-compose`.

Remember you can create new passwords as follows:

```console
openssl rand -hex 32
# Outputs something like: 99d3b1f01aa639e4a76f4fc281fc834747a543720ba4c8a8648ba755aef9be7f
```

Or, alternatively:

```console
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 6ATqOcql5J3TOWEKievJ-Oh7VyeoAVrnPnxNGB50dYY
```

```console 
# Install Git
apt-get install git
```

From `/srv`:

```shell
cd ../srv
git clone https://github.com/<project-owner>/<project-name>.git
```

**Note:** The rest of this guide - unless otherwise stated - continues from the project directory `/srv/<project-name>`.

You can pull your latest code from that directory, with:

```shell
git pull
```

### Customise your `.env` files

```console
nano .env
nano frontend/.env
```

### Set up Traefik public network

Traefik will expect a Docker "public network" named `traefik-public` to communicate with your stack(s).

This way, there will be a single public Traefik proxy that handles the communication (HTTP and HTTPS) with the outside world, and then behind that, you could have one or more stacks with different domains, even if they are on the same single server.

To create a Docker "public network" named `traefik-public` run the following command in your remote server:

```console
docker network create traefik-public
```

### Export Traefik environment variables

The Traefik Docker Compose file expects some environment variables to be set in your terminal before starting it. You can do it by running the following commands in your remote server.

* Create the username for HTTP Basic Auth, e.g.:

```console
export USERNAME=admin
```

* Create an environment variable with the password for HTTP Basic Auth, e.g.:

```console
export PASSWORD=changethis
```

* Use openssl to generate the "hashed" version of the password for HTTP Basic Auth and store it in an environment variable:

```console
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
```

To verify that the hashed password is correct, you can print it:

```console
echo $HASHED_PASSWORD
```

* Create an environment variable with the domain name for your server, e.g.:

```console
export DOMAIN=fastapi-project.example.com
```

* Create an environment variable with the email for Let's Encrypt, e.g.:

```console
export EMAIL=admin@example.com
```

**Note**: you need to set a different email, an email `@example.com` won't work.

### Start the Traefik Docker Compose

Ensure you are in the directory where you copied the Traefik Docker Compose file in your remote server:

```console
cd /srv/<project-name>
```

Now with the environment variables set and the `docker-compose.traefik.yml` in place, you can start the Traefik Docker Compose running the following command:

```console
docker compose -f docker-compose.traefik.yml up -d
```

## Deploy your project

Now that you have Traefik in place you can deploy your FastAPI project with Docker Compose.

### Set environment variables

If you haven't, review your `.env` files.

- `/.env`
- `/frontend/.env`

Most of what follows could be stored here, but you can also create ephemeral variables directly.

Set the `ENVIRONMENT`, by default `local` (for development), but when deploying to a server you would put something like `staging` or `production`:

```console
export ENVIRONMENT=production
export TAG=prod
export FRONTEND_ENV=production
export TRAEFIK_TAG=fastapi-project.example.com
export STACK_NAME=fastapi-project
```

Set the `DOMAIN`, by default `localhost` (for development), but when deploying you would use your own domain, for example:

```console
export DOMAIN=fastapi-project.example.com
```

### Ensure `frontend` `Docker` dependencies

**Important note:** The main trade-off for the minimal production build is that any NuxtJS modules declared in the [`modules:` section of the _nuxt.config.js_ file](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/frontend/nuxt.config.ts) must also be specified in the _Dockerfile_ on the `yarn add` line as shown [here](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/frontend/Dockerfile) (it's not installing from the _package.json_, which is one reason why it's smaller). 

To switch from the minimal production build to the full production build, either specify the [target build stage](https://docs.docker.com/compose/compose-file/compose-file-v3/#target) in the _docker-compose.yml_ (`target: run-start`, as is done for the local development configuration [here](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/docker-compose.override.yml)), or push Docker images from each stage to a registry, then specify the appropriate tag to be pulled (with the `TAG` environment variable).

### Deploy with Docker Compose

With the environment variables in place, you can deploy with Docker Compose:

```console
docker compose -f docker-compose.yml up -d
```

For production you wouldn't want to have the overrides in `docker-compose.override.yml`, that's why we explicitly specify `docker-compose.yml` as the file to use.

## Production URLs

These are the URLs served in production (replace `example.com` with your own):

- Frontend: https://example.com
- Backend: https://api.example.com/
- Automatic Interactive Docs (Swagger UI): https://api.example.com/docs
- Automatic Alternative Docs (ReDoc): https://api.example.com/redoc
- Adminer: https://adminer.example.com
- Flower: https://flower.example.com
- Traefik: https://traefik.example.com