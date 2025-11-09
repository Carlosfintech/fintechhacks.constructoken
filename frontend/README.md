# Nuxt.js frontend replacement for FastAPI base project generator

## What is it?

This project is for developers looking to accelerate their next web development project with a FastAPI/NuxtJS base project generator. Build and maintain full-feature progressive web applications using Python on the backend / Typescript on the frontend, with the complex-but-routine aspects of auth 'n auth, and component and deployment configuration, taken care of, including interactive API documentation. 

## Setup

Make sure to install the dependencies:

```console
# yarn
yarn install

# npm
npm install
```

## Development

Start the development server on http://localhost:3000

```console
# yarn
yarn dev

# npm
npm run dev
```

## Production

Build the application for production:

```console
# yarn 
yarn build

# npm
npm run build
```

Locally preview production build:

```console
#yarn
yarn preview

# npm
npm run preview
```

Checkout the [deployment documentation](https://v3.nuxtjs.org/guide/deploy/presets) for more information.

## Docker

A [Docker](https://www.docker.com/) configuration is also provided. The _Dockerfile_ is divided into four [build stages](https://docs.docker.com/develop/develop-images/multistage-build/):

1. `build`:
   - Copy files from the repo into the Docker container
   - Install dependencies from _package.json_ with Yarn
   - Build the Nuxt.js app with [server-side rendering](https://nuxtjs.org/docs/2.x/concepts/server-side-rendering) (SSR) in [standalone mode](https://nuxtjs.org/docs/2.x/configuration-glossary/configuration-build#standalone)
2. `run-dev`: use the build stage to run the dev server, which can hot-reload within the Docker container if the source code is mounted
3. `run-start`: use the build stage to run [`nuxt start`](https://nuxtjs.org/docs/2.x/get-started/commands), with all dependencies from the build
4. `run-minimal`: this image is less than 1/6 the size of the others (262 MB vs. 1.72 GB)
   - Pull a Node.js image running on Alpine Linux
   - Copy the built Nuxt.js app from the `build` stage, without `node_modules`
   - Install `nuxt-start`, with the minimal runtime for Nuxt.js (needed in addition to the inlined dependencies from standalone mode)
   - Run the `nuxt start` command using the `nuxt-start` module to start the SSR application

**Important note:** The main trade-off for the minimal production build is that any NuxtJS modules declared in the [`modules:` section of the _nuxt.config.js_ file](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/frontend/nuxt.config.ts) must also be specified in the _Dockerfile_ on the `yarn add` line as shown [here](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/frontend/Dockerfile) (it's not installing from the _package.json_, which is one reason why it's smaller). 

To switch from the minimal production build to the full production build, either specify the [target build stage](https://docs.docker.com/compose/compose-file/compose-file-v3/#target) in the _docker-compose.yml_ (`target: run-start`, as is done for the local development configuration [here](https://codeberg.org/whythawk/base-fastapi-nuxt-project/src/branch/main/docker-compose.override.yml)), or push Docker images from each stage to a registry, then specify the appropriate tag to be pulled (with the `TAG` environment variable).

## Licence

This project is licensed under the terms of the [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.en.html) license.
