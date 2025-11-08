# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Constructoken** is a hackathon prototype demonstrating conditional recurring payments with Buy Now Pay Later (BNPL) functionality using the Rafiki/Interledger payment infrastructure. The system orchestrates recurring payments from migrant workers to construction projects in Mexico, with automatic BNPL activation when users meet payment milestones.

This repository contains:
- **`/backend`**: Python FastAPI backend that orchestrates payments via Rafiki
- **`/rafiki`**: Submodule of the Rafiki Interledger implementation (serves as payment infrastructure)

### Key Business Logic

The BNPL flow works as follows:
1. User commits to 10 payments of $100 MXN each ($1,000 total) to fund a construction project
2. After 8 successful payments ($800), if the user qualifies for BNPL:
   - The system revokes the original payment grant (stops payments 9-10)
   - Capital marketplace finances the remaining $200 MXN to complete the project
   - A new grant is created for the user to repay the marketplace in 2 installments

## High-Level Architecture

The system has three main actors coordinated by the backend:

1. **Pagador (Payer)**: Migrant worker making payments in USD
2. **Receptor (Receiver/FINSUS)**: Construction project receiving funds in MXN
3. **Capital**: Marketplace that provides BNPL financing

The backend (`/backend`) acts as an orchestrator that:
- Creates IncomingPayments and Quotes via Rafiki GraphQL Admin API
- Executes OutgoingPayments to move funds between wallet addresses
- Monitors payment webhooks to trigger BNPL logic at the 8th payment
- Manages state and business logic while Rafiki handles the actual payment infrastructure

Rafiki (`/rafiki`) provides:
- Open Payments APIs for payment initiation
- GNAP authorization server for grants
- ILP connector for cross-currency settlements (USD → MXN)
- TigerBeetle for high-performance accounting

## Development Commands

### Backend (Python FastAPI)

```bash
cd backend

# Setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Configure Rafiki wallets (must run AFTER Rafiki local environment is up)
python setup_wallets.py

# Run the backend server
python main.py
# Server runs at http://localhost:8000

# Run the full demo (simulates complete payment flow)
python demo.py
```

### Rafiki Local Environment

```bash
cd rafiki

# Install dependencies (first time only)
nvm use
corepack enable
pnpm i

# Initialize git submodules (required for Open Payments specs)
git submodule update --init --recursive

# Start local playground with TigerBeetle accounting
pnpm localenv:compose up

# Start with PostgreSQL accounting instead
pnpm localenv:compose:psql up

# Stop and clean up
pnpm localenv:compose down
pnpm localenv:compose down --volumes  # Also remove database volumes
```

**Important**: Always start Rafiki localenv BEFORE running `backend/setup_wallets.py` or the backend server.

### Rafiki Development

```bash
cd rafiki

# Build all packages
pnpm -r build

# Build specific package
pnpm --filter backend build

# Run tests for specific package
pnpm --filter backend test

# Run all tests (sequential for stability)
pnpm -r --workspace-concurrency=1 test

# Lint and format
pnpm format           # Auto-fix
pnpm checks           # Check without fixing
```

## Key Files and Their Roles

### Backend (`/backend`)

- **`main.py`**: FastAPI application with endpoints:
  - `POST /start-project-funding`: Initiates recurring payment setup
  - `POST /execute-payment/{project_id}`: Manually triggers a payment (for demo)
  - `POST /rafiki-webhook`: **Critical** - Receives payment completion events and triggers BNPL logic
  - `GET /project-status/{project_id}`: Query project state

- **`rafiki_client.py`**: GraphQL client wrapping all Rafiki Admin API operations
  - `create_incoming_payment()`: Creates payment destinations
  - `create_quote()`: Calculates exchange rates (USD → MXN)
  - `create_outgoing_payment()`: Executes payments
  - `revoke_grant()`: Cancels payment authorization (used when BNPL triggers)

- **`config.py`**: Centralized configuration
  - Loads `rafiki_config.json` with wallet IDs created by `setup_wallets.py`
  - Business rules: payment amounts, BNPL trigger point (payment #8)
  - Connection URLs for Rafiki services

- **`models.py`**: Pydantic data models for validation and API contracts

- **`database.py`**: In-memory storage (dict-based for prototype)
  - In production, replace with PostgreSQL/SQLAlchemy

- **`setup_wallets.py`**: One-time setup script that creates three WalletAddresses in Rafiki via GraphQL and saves their IDs to `rafiki_config.json`

- **`demo.py`**: End-to-end simulation demonstrating the full BNPL flow

### Rafiki (`/rafiki`)

This is a git submodule from https://github.com/interledger/rafiki. The local environment (`rafiki/localenv`) runs:

- **Cloud Nine Wallet** (ports 3000-3010): Primary mock ASE
  - Backend Admin API: `http://localhost:3001/graphql`
  - Open Payments API: `http://localhost:3000`
  - Auth API: `http://localhost:3006`
  - Rafiki Admin UI: `http://localhost:3010`

- **Happy Life Bank** (ports 4000-4010): Secondary mock ASE for testing cross-ASE payments

The backend interacts primarily with the **Backend Admin API** at port 3001 via GraphQL.

## Important Development Notes

### GraphQL API Usage

All Rafiki operations use GraphQL mutations/queries. The `RafikiClient` class in `rafiki_client.py` contains the complete GraphQL queries. When adding new Rafiki operations:

1. Consult Rafiki Admin API docs: https://rafiki.dev/apis/graphql/admin-api-overview
2. Add the GraphQL query/mutation to `RafikiClient`
3. Return the relevant response data

### Webhook Event Handling

The webhook endpoint (`/rafiki-webhook`) is the **core** of the BNPL logic. It receives events like:
- `incoming_payment.completed`: Payment received
- `outgoing_payment.completed`: Payment sent

The critical logic in `handle_payment_completed()` (main.py:298):
1. Identifies which project the payment belongs to
2. Updates payment counter
3. Checks if BNPL trigger condition is met (8th payment + user qualifies)
4. Executes `execute_bnpl_logic()` which orchestrates the grant revocation and capital financing

### Configuration Flow

1. Start Rafiki: `cd rafiki && pnpm localenv:compose up`
2. Create wallets: `cd backend && python setup_wallets.py`
   - This creates three WalletAddresses via GraphQL
   - Saves IDs to `rafiki_config.json`
3. Start backend: `python main.py`
   - Loads `rafiki_config.json` for wallet IDs
   - Backend is now ready to orchestrate payments

### Testing the Full Flow

```bash
# Terminal 1: Start Rafiki
cd rafiki && pnpm localenv:compose up

# Terminal 2: Setup and run backend
cd backend
python setup_wallets.py
python main.py

# Terminal 3: Run demo
cd backend
python demo.py
```

The demo script will:
- Create a test project
- Execute 8 payments from Payer → Receiver
- Automatically trigger BNPL after the 8th payment
- Show Capital financing the remaining $200
- Display final state

## Currency and Amounts

All amounts use **centavos** (scale=2) as integers:
- $100 MXN = 10000 centavos
- $1000 MXN = 100000 centavos

The Rafiki Admin API expects amounts as strings in the smallest unit, so the client converts Python ints to strings.

## Debugging Rafiki

Rafiki services expose debuggers on ports 9229-9232 (see `rafiki/localenv/README.md`). Access container logs:

```bash
cd rafiki
docker compose -f localenv/cloud-nine-wallet/docker-compose.yml \
  -f localenv/happy-life-bank/docker-compose.yml \
  -f localenv/merged/docker-compose.yml logs -f
```

## Common Issues

**Issue**: `setup_wallets.py` fails with connection errors
**Solution**: Ensure Rafiki localenv is running first (`pnpm localenv:compose up`)

**Issue**: Backend can't find wallet IDs (shows "PENDING")
**Solution**: Run `python setup_wallets.py` to create `rafiki_config.json`

**Issue**: Webhooks not received
**Solution**: The current prototype uses manual payment execution via `/execute-payment/{project_id}`. True webhooks require configuring Rafiki to send events to `http://host.docker.internal:8000/rafiki-webhook`

**Issue**: TigerBeetle container exits with code 137
**Solution**: Increase Docker memory limit (see rafiki/localenv/README.md)
