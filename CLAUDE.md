# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hop Sauna is a social marketplace framework built on FastAPI (Python 3.12) and Nuxt/Vue 3 (TypeScript). The project integrates ActivityPub for federated social features and Open Payments for financial transactions. It's designed as a full-stack progressive web application with Docker Compose orchestration.

## Architecture

### Backend (FastAPI)
- **Main entry**: `backend/app/app/main.py` - FastAPI app initialization with CORS, static media mounting
- **API versioning**: All API routes under `/v1` prefix (defined in `settings.API_V1_STR`)
- **Database**: PostgreSQL with SQLAlchemy 2.0, ULID-based identifiers instead of UUID
- **Authentication**: OAuth2 JWT with argon2 hashing, magic link + TOTP support
- **CRUD pattern**: Generic CRUD operations via `app/crud/base.py` inheritance
- **Background tasks**: Celery worker with RabbitMQ queue and Redis cache
- **Configuration**: Pydantic settings in `app/core/config.py` with `.env` file support

### Frontend (Nuxt 3)
- **State management**: Pinia with persistence via pinia-plugin-persistedstate
- **Validation**: Vee-Validate 4 for forms
- **Styling**: TailwindCSS 4.0 with HeadlessUI and HeroIcons
- **Routing**: File-based routing with middleware for auth/authorization
- **Content**: Nuxt Content for markdown blog pages

### Key API Endpoints Structure
Routes are organized in `backend/app/app/api/api_v1/endpoints/`:
- `/creators` - User/creator management
- `/actor` - ActivityPub actor operations
- `/instance` - Instance configuration
- `/openpayments` - Open Payments integration
- `/merchant` - Payment processing
- `/proxy` - Proxy services
- `/generate` - Generation utilities
- `/auth` - OAuth authentication (root-level, not under /v1)
- `/.well-known` - WebFinger and ActivityPub discovery (root-level)

### Database Models Organization
- `app/models/activitypub/` - ActivityPub entities (actors, statuses, follows, activities)
- `app/models/openpayments/` - Payment entities (wallets, orders, receipts, recipients)
- `app/models/product/` - E-commerce entities
- Base models use SQLAlchemy 2.0 declarative style with ULID primary keys

## Development Commands

### Initial Setup
```bash
# Generate project from template (optional)
pipx run copier copy https://codeberg.org/whythawk/base-fastapi-nuxt-project <project-name> --trust

# Generate secure keys for .env
openssl rand -hex 32
# or
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Docker Environment
```bash
# Build all containers (first time or after dependency changes)
docker compose build --no-cache

# Start all services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f worker
```

### Backend Development
```bash
cd backend/app

# Setup Python environment with Hatch
hatch env prune  # Clean old environments
hatch env create production  # or 'development' for dev dependencies
hatch shell  # Activate environment

# Run linting/formatting
hatch run lint:fmt  # Format with black and isort
hatch run lint:style  # Check style

# Database migrations (Alembic)
docker compose exec backend bash
alembic revision --autogenerate -m "description"
alembic upgrade head

# Start Jupyter Lab (for algorithmic development)
docker compose exec backend bash
$JUPYTER  # Environment variable configured in docker-compose.override.yml
```

### Frontend Development
```bash
cd frontend

# Install dependencies
yarn install

# Run dev server (NOT in Docker - for live reload)
yarn dev  # Runs at http://localhost:3000

# Build for production
yarn build

# Preview production build
yarn preview
```

### Testing
```bash
# Backend tests
cd backend/app
hatch run pytest

# Run tests in Docker
docker compose exec backend pytest
```

## Development URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost
- Interactive API Docs (Swagger): http://localhost/docs
- Alternative API Docs (ReDoc): http://localhost/redoc
- Adminer (DB management): http://localhost:8080
- Flower (Celery monitoring): http://localhost:5555
- Mailcatcher (email testing): http://localhost:1080
- Traefik Dashboard: http://localhost:8090

## Important Configuration Notes

### Environment Variables
- Main `.env` at project root - backend, database, Redis, SMTP settings
- `frontend/.env` - frontend-specific settings (API endpoints, domain config)
- CORS origins in `.env` as `BACKEND_CORS_ORIGINS` (comma-separated string or JSON array)

### Development vs Production
- **Development**: Uses `docker-compose.override.yml` which:
  - Disables frontend Docker container (run with `yarn dev` instead for live reload)
  - Mounts backend code as volumes for live reload
  - Uses Uvicorn instead of Gunicorn
  - Enables Jupyter Lab on port 8888
  - Uses Mailcatcher instead of real SMTP
  - Exposes all service ports directly

- **Production**: Uses base `docker-compose.yml` with Traefik for routing

### Worker Container
Changes to backend code require restarting the worker container:
```bash
docker compose restart worker
```

FastAPI backend auto-reloads, but Celery worker does not.

## Special Features

### ActivityPub Integration
- Full Bovine integration for ActivityPub protocol
- Models for actors, statuses, follows, activities in `app/models/activitypub/`
- WebFinger discovery at `/.well-known/webfinger`
- Note: UI for ActivityPub features is incomplete (see README roadmap)

### Open Payments
- SDK integration complete in `app/open_payments_sdk/`
- Wallet address support for payment pointers
- Test credentials configured via environment variables (`TEST_SELLER_WALLET`, etc.)
- Note: UI for product management is incomplete (see README roadmap)

### Authentication Flow
- Magic link (email-based) as primary method
- Optional TOTP (Time-based One-Time Password) for 2FA
- Password fallback available
- Cookie-based with access + refresh tokens
- Access tokens expire in 5 minutes, refresh tokens don't expire but must be revoked

### Media Storage
Static media served from local directory defined in `settings.API_MEDIA_STR`. Can be migrated to CDN/S3 in production.

## Common Patterns

### Adding New API Endpoint
1. Create endpoint file in `backend/app/app/api/api_v1/endpoints/`
2. Import and register router in `backend/app/app/api/api_v1/api.py`
3. Use dependency injection from `app/api/deps.py` for database sessions, auth

### Creating New Model
1. Define SQLAlchemy model in appropriate `app/models/` subdirectory
2. Create Pydantic schemas in `app/schemas/`
3. Implement CRUD operations extending `app/crud/base.py`
4. Generate Alembic migration: `alembic revision --autogenerate -m "description"`

### Frontend State Management
- Create Pinia store in `frontend/stores/`
- Use `defineStore` with setup or options syntax
- Enable persistence with `persist: true` option for state that should survive page reloads

## Known Issues

- Tests are currently broken (noted in README)
- Worker container requires manual restart after backend code changes
- Frontend Docker container disabled in dev mode - must run with `yarn dev`
- Some documentation contains legacy/erroneous information from GitHub migration
