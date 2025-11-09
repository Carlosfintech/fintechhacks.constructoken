# Hop Sauna, a social marketplace framework

This project is designed to reimagine how creators and their supporters exchange money. 

It is for developers looking to accelerate their next web development project with a FastAPI/NuxtJS base project generator. Build and maintain full-feature progressive web applications using Python on the backend / Typescript on the frontend, with the complex-but-routine aspects of auth 'n auth, and component and deployment configuration, taken care of, including interactive API documentation. 

**NOTE:** This framework template is currenty a *work in progress*. It is - with some work - ready for you to begin building with, but it is not yet complete and the documentation for customisation is not written. 
  
## Key features

This FastAPI, PostgreSQL & Nuxt repo will generate a complete web application stack as a foundation for your project development.

- **Docker Compose** integration and optimization for local development.
- **Authentication** user management schemas, models, crud and apis already built, with OAuth2 JWT token support & default hashing using `argon2`. Offers _magic link_ authentication, with password fallback, with cookie management, including `access` and `refresh` tokens.
- [**FastAPI**](https://github.com/tiangolo/fastapi) version 0.115 backend with [Inboard](https://inboard.bws.bio/) one-repo Docker images, using Python 3.12:
  - **SQLAlchemy** version 2.0 support for models.
  - **Pydantic** version 2.9 for schemas.
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
- **MailCatcher** for development email testing.
- Load balancing between frontend and backend with **Traefik** version 3.3, so you can have both under the same domain, separated by path, but served by different containers.
- Traefik integration, including Let's Encrypt **HTTPS** certificates automatic generation.

## How to use it

You can fork or clone this repository and use it as is, or customise it using [Copier](https://copier.readthedocs.io/).

- [Getting started](./docs/getting-started.md)
- [Development and installation](./docs/development-guide.md)
- [Deployment for production](./docs/deployment-guide.md)
- [Authentication and magic tokens](./docs/authentication-guide.md)
- [Websockets for interactive communication](./docs/websocket-guide.md)

## Roadmap

This template is still missing several key components:

- **Complete ActivityPub support**: Bovine integration is complete, database and schemas ready, CRUD built, but the APIs and frontend UI needs development for status updates, likes, follows, etc.
- **OpenPayments completion**: SDK integration is complete, but the UI elements for product creation / management, collaborator inclusion, and frontend UI to be done.
- **Moderation**: Full moderation component to be developed.
- **Localisation**: This is discrete from *Internationalisation* (translation) ... localisation is about specific geographically-defined products or moderation. To be completed.

## Help needed

The tests are broken and it would be great if someone could take that on. Other potential roadmap items:

- Docs updating: the migration from Github has left a significant amount of legacy and erronious information.
- Translation: docs are all in English and it would be great if those could be in other languages.
- Internationalisation: [nuxt/i18n](https://v8.i18n.nuxtjs.org/) is added, but the sample pages are not all translated.
- Code review and optimisation: both the front- and backend stacks have seen some big generational changes, so would be good to have more eyes on the updates to this stack.

## Background and funding

[Gavin Chait](https://whythawk.com) is the lead developer on this project, and received funding from the [Interledger Foundation](https://interledger.org/) as a [2025 Ambassador](https://interledger.org/news/introducing-2025-interledger-foundation-ambassadors-cohort).

Never heard of Interledger or Open Payments before? Or would you like to learn more? Here are some excellent places to start:

- [Interledger Website](https://interledger.org/)
- [Interledger Specs](https://interledger.org/rfcs/0027-interledger-protocol-4/)
- [Interledger Explainer Video](https://twitter.com/Interledger/status/1567916000074678272)
- [Open Payments](https://openpayments.dev/)
- [Web Monetization](https://webmonetization.org/)

## Project release notes

### 0.1.0

- Initial copy of [Base FastAPI Nuxt Project](https://codeberg.org/whythawk/base-fastapi-nuxt-project).

## License

This project is licensed under the terms of the [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.en.html) license.
