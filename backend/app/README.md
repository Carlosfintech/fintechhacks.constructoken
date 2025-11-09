# Hop Sauna

## Documentation for development

- [Getting started](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/docs/getting-started.md)
- [Development and installation](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/docs/development-guide.md)
- [Deployment for production](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/docs/deployment-guide.md)
- [Authentication and magic tokens](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/docs/authentication-guide.md)

These are the URLs served in development:

- Frontend: http://localhost:3000
- Backend: http://localhost
- Automatic Interactive Docs (Swagger UI): http://localhost/docs
- Automatic Alternative Docs (ReDoc): http://localhost/redoc
- Mailcatcher: http://localhost:1080
- Adminer: http://localhost:8080
- Flower: http://localhost:5555
- Traefik: http://localhost:8090

**Note**: The first time you start your stack, it might take a minute for it to be ready. While the backend waits for the database to be ready and configures everything. You can check the logs to monitor it.

To check the logs, run:

```console
docker compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```console
docker compose logs backend
```

If your Docker is not running in `localhost` (the URLs above wouldn't work) check the sections below on **Development with Docker Toolbox** and **Development with a custom IP**.

## Backend local development, additional details

### General workflow

By default, the dependencies are managed with [Hatch](https://hatch.pypa.io/latest/), go there and install it.

From `./backend/app/` you can install all the dependencies with:

```console
$ hatch env prune
$ hatch env create production
```

Because Hatch doesn't have a version lock file (like Poetry), it is helpful to `prune` when you rebuild to avoid any sort of dependency hell. Then you can start a shell session with the new environment with:

```console
$ hatch shell
```

Next, open your editor at `./backend/app/` (instead of the project root: `./`), so that you see an `./app/` directory with your code inside. That way, your editor will be able to find all the imports, etc. Make sure your editor uses the environment you just created with Hatch. For Visual Studio Code, from the shell, launch an appropriate development environment with:

```console
$ code .
```

Modify or add SQLAlchemy models in `./backend/app/app/models/`, Pydantic schemas in `./backend/app/app/schemas/`, API endpoints in `./backend/app/app/api/`, CRUD (Create, Read, Update, Delete) utils in `./backend/app/app/crud/`. The easiest might be to copy the ones for Items (models, endpoints, and CRUD utils) and update them to your needs.

Add and modify tasks to the Celery worker in `./backend/app/app/worker.py`.

If you need to install any additional package to the worker, add it to the file `./backend/app/worker.dockerfile`.

### Docker Compose Override

During development, you can change Docker Compose settings that will only affect the local development environment, in the file `docker-compose.override.yml`.

The changes to that file only affect the local development environment, not the production environment. So, you can add "temporary" changes that help the development workflow.

For example, the directory with the backend code is mounted as a Docker "host volume", mapping the code you change live to the directory inside the container. That allows you to test your changes right away, without having to build the Docker image again. It should only be done during development, for production, you should build the Docker image with a recent version of the backend code. But during development, it allows you to iterate very fast. Have in mind that if you have a syntax error and save the Python file, it will break and exit, and the container will stop. After that, you can restart the container by fixing the error and running again:

```console
$ docker compose up -d
```

There is also a commented out `command` override, you can uncomment it and comment the default one. It makes the backend container run a process that does "nothing", but keeps the container alive. That allows you to get inside your running container and execute commands inside, for example a Python interpreter to test installed dependencies, or start the development server that reloads when it detects changes, or start a Jupyter Notebook session.

To get inside the container with a `bash` session you can start the stack with:

```console
$ docker compose up -d
```

and then `exec` inside the running container:

```console
$ docker compose exec backend bash
```

You should see an output like:

```console
root@7f2607af31c3:/app#
```

that means that you are in a `bash` session inside your container, as a `root` creator, under the `/app` directory.

### Backend tests

> NOTE: Tests have not been updated on the current version, so these are likely to fail.

To test the backend run:

```console
$ DOMAIN=backend sh ./scripts/test.sh
```

The file `./scripts/test.sh` has the commands to generate a testing `docker-stack.yml` file, start the stack and test it.

The tests run with Pytest, modify and add tests to `./backend/app/app/tests/`.

If you use GitLab CI the tests will run automatically.

#### Local tests

Start the stack with this command:

```Bash
DOMAIN=backend sh ./scripts/test-local.sh
```
The `./backend/app` directory is mounted as a "host volume" inside the docker container (set in the file `docker-compose.dev.volumes.yml`).
You can rerun the test on live code:

```Bash
docker compose exec backend /app/tests-start.sh
```

#### Test running stack

If your stack is already up and you just want to run the tests, you can use:

```console
docker compose exec backend /app/tests-start.sh
```

That `/app/tests-start.sh` script just calls `pytest` after making sure that the rest of the stack is running. If you need to pass extra arguments to `pytest`, you can pass them to that command and they will be forwarded.

For example, to stop on first error:

```console
docker compose exec backend bash /app/tests-start.sh -x
```

#### Test Coverage

Because the test scripts forward arguments to `pytest`, you can enable test coverage HTML report generation by passing `--cov-report=html`.

To run the local tests with coverage HTML reports:

```Bash
DOMAIN=backend sh ./scripts/test-local.sh --cov-report=html
```

To run the tests in a running stack with coverage HTML reports:

```console
docker compose exec backend bash /app/tests-start.sh --cov-report=html
```

### Live development with Python Jupyter Notebooks

If you know about Python [Jupyter Notebooks](http://jupyter.org/), you can take advantage of them during local development.

The `docker-compose.override.yml` file sends a variable `env` with a value `dev` to the build process of the Docker image (during local development) and the `Dockerfile` has steps to then install and configure Jupyter inside your Docker container.

So, you can enter into the running Docker container:

```console
docker compose exec backend bash
```

And use the environment variable `$JUPYTER` to run a Jupyter Notebook with everything configured to listen on the public port (so that you can use it from your browser).

It will output something like:

```console
root@73e0ec1f1ae6:/app# $JUPYTER
[I 12:02:09.975 NotebookApp] Writing notebook server cookie secret to /root/.local/share/jupyter/runtime/notebook_cookie_secret
[I 12:02:10.317 NotebookApp] Serving notebooks from local directory: /app
[I 12:02:10.317 NotebookApp] The Jupyter Notebook is running at:
[I 12:02:10.317 NotebookApp] http://(73e0ec1f1ae6 or 127.0.0.1):8888/?token=f20939a41524d021fbfc62b31be8ea4dd9232913476f4397
[I 12:02:10.317 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[W 12:02:10.317 NotebookApp] No web browser found: could not locate runnable browser.
[C 12:02:10.317 NotebookApp]

    Copy/paste this URL into your browser when you connect for the first time,
    to login with a token:
        http://(73e0ec1f1ae6 or 127.0.0.1):8888/?token=f20939a41524d021fbfc62b31be8ea4dd9232913476f4397
```

you can copy that URL and modify the "host" to be `localhost` or the domain you are using for development (e.g. `local.dockertoolbox.tiangolo.com`), in the case above, it would be, e.g.:

```
http://localhost:8888/token=f20939a41524d021fbfc62b31be8ea4dd9232913476f4397
```

 and then open it in your browser.

You will have a full Jupyter Notebook running inside your container that has direct access to your database by the container name (`db`), etc. So, you can just run sections of your backend code directly, for example with [VS Code Python Jupyter Interactive Window](https://code.visualstudio.com/docs/python/jupyter-support-py) or [Hydrogen](https://github.com/nteract/hydrogen).

### Migrations

As during local development your app directory is mounted as a volume inside the container, you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker compose exec backend bash
```

* If you created a new model in `./backend/app/app/models/`, make sure to import it in `./backend/app/app/db/base.py`, that Python module (`base.py`) that imports all the models will be used by Alembic.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to Creator model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```

If you don't want to use migrations at all, uncomment the line in the file at `./backend/app/app/db/init_db.py` with:

```python
Base.metadata.create_all(bind=engine)
```

and comment the line in the file `prestart.sh` that contains:

```console
$ alembic upgrade head
```

If you don't want to start with the default models and want to remove them / modify them, from the beginning, without having any previous revision, you can remove the revision files (`.py` Python files) under `./backend/app/alembic/versions/`. And then create a first migration as described above.

### Development with Docker Toolbox

If you are using **Docker Toolbox** in Windows or macOS instead of **Docker for Windows** or **Docker for Mac**, Docker will be running in a VirtualBox Virtual Machine, and it will have a local IP different than `127.0.0.1`, which is the IP address for `localhost` in your machine.

The address of your Docker Toolbox virtual machine would probably be `192.168.99.100` (that is the default).

As this is a common case, the domain `local.dockertoolbox.tiangolo.com` points to that (private) IP, just to help with development (actually `dockertoolbox.tiangolo.com` and all its subdomains point to that IP). That way, you can start the stack in Docker Toolbox, and use that domain for development. You will be able to open that URL in Chrome and it will communicate with your local Docker Toolbox directly as if it was a cloud server, including CORS (Cross Origin Resource Sharing).

If you used the default CORS enabled domains while generating the project, `local.dockertoolbox.tiangolo.com` was configured to be allowed. If you didn't, you will need to add it to the list in the variable `BACKEND_CORS_ORIGINS` in the `.env` file.

To configure it in your stack, follow the section **Change the development "domain"** below, using the domain `local.dockertoolbox.tiangolo.com`.

After performing those steps you should be able to open: http://local.dockertoolbox.tiangolo.com and it will be server by your stack in your Docker Toolbox virtual machine.

Check all the corresponding available URLs in the section at the end.

### Development in `localhost` with a custom domain

You might want to use something different than `localhost` as the domain. For example, if you are having problems with cookies that need a subdomain, and Chrome is not allowing you to use `localhost`.

In that case, you have two options: you could use the instructions to modify your system `hosts` file with the instructions below in **Development with a custom IP** or you can just use `localhost.tiangolo.com`, it is set up to point to `localhost` (to the IP `127.0.0.1`) and all its subdomains too. And as it is an actual domain, the browsers will store the cookies you set during development, etc.

If you used the default CORS enabled domains while generating the project, `localhost.tiangolo.com` was configured to be allowed. If you didn't, you will need to add it to the list in the variable `BACKEND_CORS_ORIGINS` in the `.env` file.

To configure it in your stack, follow the section **Change the development "domain"** below, using the domain `localhost.tiangolo.com`.

After performing those steps you should be able to open: http://localhost.tiangolo.com and it will be server by your stack in `localhost`.

Check all the corresponding available URLs in the section at the end.

### Development with a custom IP

If you are running Docker in an IP address different than `127.0.0.1` (`localhost`) and `192.168.99.100` (the default of Docker Toolbox), you will need to perform some additional steps. That will be the case if you are running a custom Virtual Machine, a secondary Docker Toolbox or your Docker is located in a different machine in your network.

In that case, you will need to use a fake local domain (`dev.hopsauna.com`) and make your computer think that the domain is is served by the custom IP (e.g. `192.168.99.150`).

If you used the default CORS enabled domains, `dev.hopsauna.com` was configured to be allowed. If you want a custom one, you need to add it to the list in the variable `BACKEND_CORS_ORIGINS` in the `.env` file.

* Open your `hosts` file with administrative privileges using a text editor:
  * **Note for Windows**: If you are in Windows, open the main Windows menu, search for "notepad", right click on it, and select the option "open as Administrator" or similar. Then click the "File" menu, "Open file", go to the directory `c:\Windows\System32\Drivers\etc\`, select the option to show "All files" instead of only "Text (.txt) files", and open the `hosts` file.
  * **Note for Mac and Linux**: Your `hosts` file is probably located at `/etc/hosts`, you can edit it in a terminal running `sudo nano /etc/hosts`.

* Additional to the contents it might have, add a new line with the custom IP (e.g. `192.168.99.150`) a space character, and your fake local domain: `dev.hopsauna.com`.

The new line might look like:

```
192.168.99.100    dev.hopsauna.com
```

* Save the file.
  * **Note for Windows**: Make sure you save the file as "All files", without an extension of `.txt`. By default, Windows tries to add the extension. Make sure the file is saved as is, without extension.

...that will make your computer think that the fake local domain is served by that custom IP, and when you open that URL in your browser, it will talk directly to your locally running server when it is asked to go to `dev.hopsauna.com` and think that it is a remote server while it is actually running in your computer.

To configure it in your stack, follow the section **Change the development "domain"** below, using the domain `dev.hopsauna.com`.

After performing those steps you should be able to open: http://dev.hopsauna.com and it will be server by your stack in `localhost`.

Check all the corresponding available URLs in the section at the end.

### Change the development "domain"

If you need to use your local stack with a different domain than `localhost`, you need to make sure the domain you use points to the IP where your stack is set up. See the different ways to achieve that in the sections above (i.e. using Docker Toolbox with `local.dockertoolbox.tiangolo.com`, using `localhost.tiangolo.com` or using `dev.hopsauna.com`).

To simplify your Docker Compose setup, for example, so that the API docs (Swagger UI) knows where is your API, you should let it know you are using that domain for development. You will need to edit 1 line in 2 files.

* Open the file located at `./.env`. It would have a line like:

```
DOMAIN=localhost
```

* Change it to the domain you are going to use, e.g.:

```
DOMAIN=localhost.tiangolo.com
```

That variable will be used by the Docker Compose files.

* Now open the file located at `./frontend/.env`. It would have a line like:

```
VUE_APP_DOMAIN_DEV=localhost
```

* Change that line to the domain you are going to use, e.g.:

```
VUE_APP_DOMAIN_DEV=localhost.tiangolo.com
```

That variable will make your frontend communicate with that domain when interacting with your backend API, when the other variable `VUE_APP_ENV` is set to `development`.

After changing the two lines, you can re-start your stack with:

```console
docker compose up -d
```

and check all the corresponding available URLs in the section at the end.

## Frontend development

See the [frontend README](./frontend/README.md) for instructions.

### Removing the frontend

If you are developing an API-only app and want to remove the frontend, you can do it easily:

* Remove the `./frontend` directory.
* In the `docker-compose.yml` file, remove the whole service / section `frontend`.
* In the `docker-compose.override.yml` file, remove the whole service / section `frontend`.

Done, you have a frontend-less (api-only) app. 🔥 🚀

---

If you want, you can also remove the `FRONTEND` environment variables from:

* `.env`
* `.gitlab-ci.yml`
* `./scripts/*.sh`

But it would be only to clean them up, leaving them won't really have any effect either way.

### Persisting Docker named volumes

You need to make sure that each service (Docker container) that uses a volume is always deployed to the same Docker "node" in the cluster, that way it will preserve the data. Otherwise, it could be deployed to a different node each time, and each time the volume would be created in that new node before starting the service. As a result, it would look like your service was starting from scratch every time, losing all the previous data.

That's specially important for a service running a database. But the same problem would apply if you were saving files in your main backend service (for example, if those files were uploaded by your creators, or if they were created by your system).

To solve that, you can put constraints in the services that use one or more data volumes (like databases) to make them be deployed to a Docker node with a specific label. And of course, you need to have that label assigned to one (only one) of your nodes.

#### Adding services with volumes

For each service that uses a volume (databases, services with uploaded files, etc) you should have a label constraint in your `docker-compose.yml` file.

To make sure that your labels are unique per volume per stack (for example, that they are not the same for `prod` and `stag`) you should prefix them with the name of your stack and then use the same name of the volume.

Then you need to have those constraints in your `docker-compose.yml` file for the services that need to be fixed with each volume.

To be able to use different environments, like `prod` and `stag`, you should pass the name of the stack as an environment variable. Like:

```console
STACK_NAME=stag-hop-sauna-com sh ./scripts/deploy.sh
```

To use and expand that environment variable inside the `docker-compose.yml` files you can add the constraints to the services like:

```yaml
services:
  db:
    volumes:
      - 'app-db-data:/var/lib/postgresql/data/pgdata'
    deploy:
      placement:
        constraints:
          - node.labels.${STACK_NAME?Variable not set}.app-db-data == true
```

note the `${STACK_NAME?Variable not set}`. In the script `./scripts/deploy.sh`, the `docker-compose.yml` would be converted, and saved to a file `docker-stack.yml` containing:

```yaml
services:
  db:
    volumes:
      - 'app-db-data:/var/lib/postgresql/data/pgdata'
    deploy:
      placement:
        constraints:
          - node.labels.hop-sauna-com.app-db-data == true
```

**Note**: The `${STACK_NAME?Variable not set}` means "use the environment variable `STACK_NAME`, but if it is not set, show an error `Variable not set`".

If you add more volumes to your stack, you need to make sure you add the corresponding constraints to the services that use that named volume.

Then you have to create those labels in some nodes in your Docker Swarm mode cluster.

#### Adding labels manually

If you want to manually assign the constraint labels, you can do the following:

* First, connect via SSH to your Docker Swarm mode cluster.

* Then check the available nodes with:

```console
$ docker node ls

// you would see an output like:

ID                            HOSTNAME               STATUS              AVAILABILITY        MANAGER STATUS
nfa3d4df2df34as2fd34230rm *   dog.example.com        Ready               Active              Reachable
2c2sd2342asdfasd42342304e     cat.example.com        Ready               Active              Leader
c4sdf2342asdfasd4234234ii     snake.example.com      Ready               Active              Reachable
```

then chose a node from the list. For example, `dog.example.com`.

* Add the label to that node. Use as label the name of the stack you are deploying followed by a dot (`.`) followed by the named volume, and as value, just `true`, e.g.:

```console
docker node update --label-add hop-sauna-com.app-db-data=true dog.example.com
```

* Then you need to do the same for each stack version you have. For example, for staging you could do:

```console
docker node update --label-add stag-hop-sauna-com.app-db-data=true cat.example.com
```