---
title: Getting started with Hop Sauna
description: "This FastAPI, PostgreSQL, Neo4j & Nuxt 3 repo will generate a complete web application stack as a foundation for your project development."
author: Gavin Chait
publishedAt: 2023-08-13
categories: [introduction, generator]
---

# Getting started with Hop Sauna

---

Accelerate your next web development project with this FastAPI/Nuxt.js base project generator.

---

- [What is it?](#what-is-it)
- [Who is it for?](#who-is-it-for)
- [How to use it](#how-to-use-it)
- [Fork differences](#fork-differences)
- [License](#license)

---

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

## Fork differences

The original objective of this fork was to maintain parity with the [Full Stack FastAPI and PostgreSQL Base Project Generator](https://github.com/tiangolo/full-stack-fastapi-postgresql) but update it to bring it up to current stack versions, fixes, and with a complete auth 'n auth system.

With the most recent updates to the base stack (as of 2024), Sebastián has made some fairly dramatic changes and these two stacks are no longer compatible. This table presents a summary of the major differences:

| This base stack                  | Tiangolo base stack     |
| :------------------------------- | :---------------------- |
| SQLAlchemy & Pydantic            | SqlModel                |
| Postgresql 17 & Adminer          | Postgresql 12 & Adminer |
| Celery & RabbitMQ task queue     | -                       |
| Redis caching                    | -                       |
| NuxtJS frontend                  | React frontend          |
| Tailwind CSS                     | Bootstrap CSS           |

This stack also has a much more sophisticated and feature-complete auth 'n auth system which is a requirement for any web app. A basic implementation of `i18n` support is available in both `frontend` and `backend`.

## Licence

This project is licensed under the terms of the [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.en.html) license.
