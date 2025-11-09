# Getting started with Hop Sauna

1. [Getting started](getting-started.md)
2. [Development and installation](development-guide.md)
3. [Deployment for production](deployment-guide.md)
4. [Authentication and magic tokens](authentication-guide.md)
5. [Websockets for interactive communication](websocket-guide.md)

---

## Contents

- [What is it?](#what-is-it)
- [Who is it for?](#who-is-it-for)
- [What does it look like?](#what-does-it-look-like)
- [How to use it](#how-to-use-it)
- [Release notes](#release-notes)
- [License](#license)

## What is it?

This FastAPI, PostgreSQL & Nuxt repo will generate a complete web application stack as a foundation for your project development.

- **Docker Compose** integration and optimization for local development.
- **Authentication** user management schemas, models, crud and apis already built, with OAuth2 JWT token support & default hashing using `argon2`. Offers _magic link_ authentication, with password fallback, with cookie management, including `access` and `refresh` tokens.
- [**FastAPI**](https://github.com/tiangolo/fastapi) version 0.115 backend with [Inboard](https://inboard.bws.bio/) one-repo Docker images, using Python 3.12:
  - **SQLAlchemy** version 2.0 support for models.
  - **Pydantic** version 2.9 for schemas.
  - **Metadata Schema** based on [Dublin Core](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#section-3) for inheritance.
  - **Common CRUD** support via generic inheritance.
  - **Standards-based**: Based on (and fully compatible with) the open standards for APIs: [OpenAPI](https://github.com/OAI/OpenAPI-Specification) and [JSON Schema](http://json-schema.org/).
  - **MJML** templates for common email transactions.
  - [**Many other features**]("https://fastapi.tiangolo.com/features/"): including automatic validation, serialization, interactive documentation, etc.
- [**Nuxt/Vue 3**](https://nuxt.com/) frontend using TypeScript:
  - **Authorisation** via middleware for page access, including logged in or superuser.
  - **Model blog** project, with [Nuxt Content](https://content.nuxtjs.org/) for writing Markdown pages.
  - **Form validation** with [Vee-Validate 4](https://vee-validate.logaretm.com/v4/).
  - **State management** with [Pinia](https://pinia.vuejs.org/), and persistance with [Pinia PersistedState](https://prazdevs.github.io/pinia-plugin-persistedstate/).
  - **CSS and templates** with [TailwindCSS](https://tailwindcss.com/), [HeroIcons](https://heroicons.com/), and [HeadlessUI](https://headlessui.com/).
- **PostgreSQL** database.
- **Adminer** for PostgreSQL database management.
- **Celery** worker that can import and use models and code from the rest of the backend selectively.
- **Flower** for Celery jobs monitoring.
- **Redis** for caching.
- Load balancing between frontend and backend with **Traefik** version 3.3, so you can have both under the same domain, separated by path, but served by different containers.
- Traefik integration, including Let's Encrypt **HTTPS** certificates automatic generation.

## Who is it for?

This project is a rock-solid foundation on which to build complex web applications which need parallel processing, scheduled event management, and a range of relational and graph database support. The base deployment takes up about 12Gb drive space, and requires about 4Gb of memory to build. 

This is **not** a light-weight system to deploy a blog or simple content-management-system. There are [easier ways to run a blog](https://github.com/myles/awesome-static-generators).

It is for developers looking to build and maintain full feature progressive web applications that can run online, or offline, want the complex-but-routine aspects of auth 'n auth, and component and deployment configuration taken care of.

## How to use it

You can fork or clone this repository and use it as is.

### Installing for local development

You can customise the deployment by generating a new project using [Copier](https://copier.readthedocs.io/), and then building with Docker compose, takes about 20 minutes.

- [Development and installation](development-guide.md)

### Deploying for production

This stack can be adjusted and used with several deployment options that are compatible with Docker Compose, but it is designed to be used with a Traefik main load balancer proxy handling automatic HTTPS certificates.

- [Deployment for production](deployment-guide.md)

### Authentication with magic and TOTP

Time-based One-Time Password (TOTP) authentication extends the login process to include a challenge-response component where the user needs to enter a time-based token after their preferred login method.

- [Authentication and magic tokens](authentication-guide.md)

## What does it look like?

### App landing page

![Landing page](../img/landing.png)

### Dashboard Login

![Magic-link login](../img/login.png)

### Dashboard User Management

![Moderator user management](../img/dashboard.png)

### Interactive API documentation

![Interactive API docs](../img/redoc.png)

### Enabling two-factor security (TOTP)

![Enabling TOTP](../img/totp.png)

## Release Notes

See notes and [releases](https://codeberg.org/whythawk/base-fastapi-nuxt-project/releases). The last four release notes are listed here:

### 0.10.0

General updates:
- Traefik 2.11 -> 3.3
- PGAdmin -> Adminer
- Redis 7.4 (new)
- Mailcatcher (new, `docker-compose.override.yml` only)
- Cookiecutter -> Copier
- Removed Docker Swarm

Updates to `backend`:
- Python 3.11 -> 3.12
- FastAPI 0.109 -> 0.115 (Inboard 0.68 -> 0.72)
- Pydantic 2.7.1 -> 2.9
- UUID -> [Universally Unique Lexicographically Sortable Identifier (ULID)](https://github.com/ulid/spec)

Updates to `frontend`:
- Node 18.17 -> 22.14
- NuxtJS 3.11.2 -> 3.15.4
- Nuxtjs i18n 8.3.1 -> 9.2.1
- Nuxt Content 2.13 -> 3.3
- Tailwind 3.4 -> 4.0

Migration to [Codeberg.org](https://codeberg.org).

### 0.9.0

Updates to `backend`:
- FastAPI 0.99 -> 0.109 (Inboard 0.51 -> 0.68)
- Pydantic 1.10 -> 2.7.1

Updates to `frontend`:
- NuxtJS 3.6.5 -> 3.11.2
- Nuxtjs i18n 8.0.0 RC -> 8.3.1

The Pydantic change is dramatic, so please revise their [migration guide](https://docs.pydantic.dev/2.7/migration/). Similarly, [nuxt/i18n](https://i18n.nuxtjs.org/docs/getting-started) has some major quality of life improvements.

### 0.8.2

Fixing [#39](https://github.com/whythawk/full-stack-fastapi-postgresql/issues/39), thanks to @a-vorobyoff:

- Exposing port 24678 for Vite on frontend in development mode.
- Ensuring Nuxt content on /api/_content doesn't interfere with backend /api/v routes.
- Checking for password before hashing on user creation.
- Updating generated README for Hatch (after Poetry deprecation).
- Minor fixes.

[Historic changes from fork](https://github.com/whythawk/full-stack-fastapi-postgresql/releases). 
[Historic changes from original](https://github.com/tiangolo/full-stack-fastapi-postgresql#release-notes)

## License

This project is licensed under the terms of the [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.en.html) license.
