# Development and cookiecutter installation

1. [Getting started](getting-started.md)
2. [Development and installation](development-guide.md)
3. [Deployment for production](deployment-guide.md)
4. [Authentication and magic tokens](authentication-guide.md)
5. [Websockets for interactive communication](websocket-guide.md)

---

## Contents

- [Run Copier](#run-copier)
- [Generate passwords](#generate-passwords)
- [Input variables](#input-variables)
- [Local development](#local-development)
- [Starting Jupyter Lab](#starting-jupyter-lab)
- [Development URLs](#development-urls)

This project is hosted at [Codeberg.org](https://codeberg.org) which tends to favour open source projects. If you want to create a private repository for your project, you will need to clone this repo, then create a new repository and manage as you prefer.

Since this project is intended as a base stack for development, the expectation is that your code will quickly diverge from the original.

## Run Copier

You can ignore this and simply clone the base project and customise as you wish. 

```console
git clone https://codeberg.org/whythawk/base-fastapi-nuxt-project <project-name>
```

However, [Copier](https://copier.readthedocs.io/) provides a way for systematically updating a project template. You can even run this after you have cloned, if you wish, just change the link references to your source folder.

Install as follows:

```console
pipx install copier
```

Decide on a name for your repository / project, and create a directory for it. Then `cd` to that directory and run:

```console
cd <project>/<directory>
copier copy https://codeberg.org/whythawk/base-fastapi-nuxt-project <project-name> --trust
```

Replacing `<project name>` with whatever you wish to call it.

Alternatively, if you have `pipx` installed, you don't need to install `copier`:

```console
pipx run copier copy https://codeberg.org/whythawk/base-fastapi-nuxt-project <project-name> --trust
```

**Note:** the `--trust` option is necessary to be able to execute a [post-creation script](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/.copier/update_dotenv.py) that updates your `.env` files.

Copier will then take you through the `.env` and project data requirements.

**In case of error:** You may get an error `Command 'python .copier/update_dotenv.py' returned non-zero exit status 127` which relates to this [issue](https://github.com/fastapi/full-stack-fastapi-template/issues/733). The recommended solution is to first run: `apt-get install python-is-python3`

## Generate passwords

You will be asked to provide passwords and secret keys for several components. Open another terminal and run:

```console
openssl rand -hex 32
# Outputs something like: 99d3b1f01aa639e4a76f4fc281fc834747a543720ba4c8a8648ba755aef9be7f
```

Or, alternatively:

```console
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 6ATqOcql5J3TOWEKievJ-Oh7VyeoAVrnPnxNGB50dYY
```

Copy the contents and use that as password / secret key. And run that again to generate another secure key.

## Input variables

Copier will ask you for data on a long list of fields which will be used to populate variables across the project, customising it for you out the box. You might want to have these on hand before generating the project. However, you can also always customise the `.env` files at any time:

```console
nano .env
nano frontend/.env
```

The [input variables](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/copier.yml), with their default values (some auto generated) are:

The following can all be found in `.env`:

- `project_name`: The name of the project, shown to API users
- `stack_name`: The name of the stack used for Docker Compose labels (no spaces)
- `secret_key`: The secret key for the project, used for security
- `totp_secret_key`: The TOTP secret key for the project, used for security
- `first_admin`: The email of the first admin
- `first_admin_password`: The password of the first admin
- `smtp_port`: Port to use to send emails via SMTP. By default `587`.
- `smtp_host`: Host to use to send emails, it would be given by your email provider, like Mailgun, Sparkpost, etc.
- `smtp_user`: The user to use in the SMTP connection. The value will be given by your email provider.
- `smtp_password`: The password to be used in the SMTP connection. The value will be given by the email provider.
- `emails_from_email`: The email account to use as the sender in the notification emails, it could be something like `info@your-custom-domain.com`.
- `emails_from_name`: The email account name to use as the sender in the notification emails, it could be something like `Symona Adaro`.
- `emails_to_email`: The email account to use as the recipient for `contact us` emails, it could be something like `requests@your-custom-domain.com`.
- `postgres_password`: Postgres database password. Use the method above to generate it.
- `flower_basic_auth`: Basic HTTP authentication for flower, in the form`user:<password>`. By default: "`admin:changethis`".
- `redis_password`: Redis password.
- `sentry_dsn`: Key URL (DSN) of Sentry, for live error reporting. You can use the open source version or a free account. E.g.: `https://1234abcd:5678ef@sentry.example.com/30`.

You will also find a few more settings to change as you enter `production`, but which are at their `development` defaults:

- In `.env`:
    - `FRONTEND_HOST`: Used by the backend to generate links in emails to the frontend.
    - `TRAEFIK_TAG`: Used by Traefik for tags.
    - `BACKEND_CORS_ORIGINS`: Origins (domains, more or less) that are enabled for CORS (Cross Origin Resource Sharing). This allows a frontend in one domain (e.g. `https://dashboard.example.com`) to communicate with this backend, that could be living in another domain (e.g. `https://api.example.com`). It can also be used to allow your local frontend (with a custom `hosts` domain mapping, as described in the project's `README.md`) that could be living in `http://dev.example.com:8080` to communicate with the backend at `https://stag.example.com`. Notice the `http` vs `https` and the `dev.` prefix for local development vs the "staging" `stag.` prefix. By default, it includes origins for production, staging and development, with ports commonly used during local development by several popular frontend frameworks (Vue with `:8080`, React, Angular). **NOTE** that this is presented as a comma-separated string, e.g. `"http://localhost,http://localhost:4200,http://localhost:8000"`
- In `frontend/.env`:
    - `VUE_APP_NAME`: Equivalent to the project name, and for making it available in the `frontend`.
    - `VUE_APP_ENV`: Set this appropriately, default is `development`.
    - `BASE_URL`: The URI for the `frontend`, set for production, and default is `http://localhost:3000`
    - `VUE_APP_DOMAIN_API`: The domain url used by the frontend app for backend api calls. If deploying a localhost development environment, likely to be `http://localhost/api/v1`
    - `VUE_APP_DOMAIN_WS`: The domain url used by the frontend app for backend websocket calls. If deploying a localhost development environment, likely to be `ws://localhost/api/v1`
    - `VUE_APP_DOMAIN_ROOT`: The domain url used by the frontend app for backend calls. If deploying a localhost development environment, likely to be `http://localhost/api`

## Local development

Once customised, you will have a folder populated with the base project and all input variables. Change into the project folder and run the `docker-compose` script to build the project containers:

```console
docker compose build --no-cache
```

And start them:

```console
docker compose up -d 
```

By default, `backend` Python dependencies are managed with [Hatch](https://hatch.pypa.io/latest/). From `./backend/app/` you can install all the dependencies with:

```console
$ hatch env prune
$ hatch env create production
```

Because Hatch doesn't have a version lock file (like Poetry), it is helpful to `prune` when you rebuild to avoid any sort of dependency hell. Then you can start a shell session with the new environment with:

```console
$ hatch shell
```

Make sure your editor uses the environment you just created with Hatch. For Visual Studio Code, from the shell, launch an appropriate development environment with:

```console
$ code .
```

**NOTE:** The Nuxt image does not automatically refresh while running in development mode. Any changes will need a rebuild. This gets tired fast, so it's easier to run Nuxt outside Docker and call through to the `backend` for API calls. You can then view the frontend at `http://localhost:3000` and the backend api endpoints at `http://localhost/redoc`. This problem won't be a concern in production.

By **default**, `docker-compose.override.yml` does **NOT** start a Nuxt image. Instead, change into the `/frontend` folder, and:

```console
yarn install
yarn dev
```

FastAPI `backend` updates will refresh automatically, but the `worker` container must be restarted before changes take effect.

## Starting Jupyter Lab

If you like to do algorithmic development and testing in Jupyter Notebooks, then launch the `backend` terminal and start Jupyter as follows:

```console
docker compose exec backend bash
```

From the terminal:

```console
$JUPYTER
```

Copy the link generated into your browser and start.

**NOTE:** Notebooks developed in the container are not saved outside, so remember to copy them for persistence. You can do that from inside Jupyter (download), or:

```console
docker cp <containerId>:/file/path/within/container /host/path/target
```

Or share a folder via `docker-compose.override.yml`.

At this point, development is over to you.

## Development URLs

These are the URLs served in development:

- Frontend: http://localhost:3000
- Backend: http://localhost
- Automatic Interactive Docs (Swagger UI): http://localhost/docs
- Automatic Alternative Docs (ReDoc): http://localhost/redoc
- Mailcatcher: http://localhost:1080
- Adminer: http://localhost:8080
- Flower: http://localhost:5555
- Traefik: http://localhost:8090