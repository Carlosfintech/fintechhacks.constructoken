# 🏗️ Constructoken - Interledger Hackathon 2025

**Plataforma de ahorro y pagos transfronterizos para construcción de viviendas usando Open Payments**

---

## 📋 Tabla de Contenidos

- [Resumen del Proyecto](#resumen-del-proyecto)
- [Caso de Uso del Hackathon](#caso-de-uso-del-hackathon)
- [Arquitectura Técnica](#arquitectura-técnica)
- [Stack Tecnológico](#stack-tecnológico)
- [Configuración e Instalación](#configuración-e-instalación)
- [Flujos de Pago](#flujos-de-pago)
- [API Endpoints](#api-endpoints)
- [Configuración del Sandbox](#configuración-del-sandbox)
- [Pruebas](#pruebas)
- [Documentación Adicional](#documentación-adicional)

---

## 🎯 Resumen del Proyecto

**Constructoken** es un marketplace que ayuda a personas en México (especialmente familias de migrantes) a autoconstruir sus viviendas mediante una plataforma de planificación financiera y pagos transfronterizos.

### Problema

- **Acceso limitado a financiamiento** para construcción de vivienda en México
- **Fugas de dinero** cuando los migrantes envían remesas a familiares
- **Falta de planificación** financiera para proyectos de construcción por etapas

### Solución

- Plataforma para **planificar proyectos por etapas**
- **Wallet de ahorro** integrada con FINSUS (México)
- **Pagos recurrentes automatizados** desde USA hacia cuenta de ahorro
- **Compra directa de materiales** cuando se alcanza la meta de ahorro
- Integración con **Open Payments** para transacciones transparentes y eficientes

---

## 🚀 Caso de Uso del Hackathon

### "Pagos Recurrentes para Ahorro y Compra de Materiales"

Un migrante en Estados Unidos quiere construir una casa en México, pero lo hará por etapas debido a la falta de acceso a crédito hipotecario.

#### Flujo del Usuario

1. **Planificación**: El migrante divide su proyecto en etapas (ej: Cimentación, Muros, Techo)
2. **Meta Financiera**: Cada etapa se convierte en una meta de ahorro (ej: $1,000 MXN)
3. **Pagos Recurrentes** (Fase I - USD → MXN):
   - Domicilia pagos semanales desde su cuenta en USA (USD)
   - Los fondos se convierten automáticamente y se depositan en su wallet Finsus (MXN)
   - Ejemplo: 10 pagos de $100 MXN = $1,000 MXN total
4. **Compra de Materiales** (Fase II - MXN → Merchant):
   - Cuando alcanza su meta, puede comprar materiales
   - Pago único desde wallet Finsus al proveedor de materiales
   - Los materiales se entregan directamente al lugar de construcción

---

## 🏛️ Arquitectura Técnica

### Actores del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CONSTRUCTOKEN SYSTEM                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐                                                   │
│  │   MIGRANTE   │                                                   │
│  │   (USA)      │                                                   │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         │ ① Configura pagos recurrentes                            │
│         ▼                                                           │
│  ┌────────────────────┐      FASE I: USD → MXN                     │
│  │  US Wallet (USD)   │─────(Recurring Payments)────┐              │
│  │  ASE Estados Unidos│                             │              │
│  └────────────────────┘                             ▼              │
│                                          ┌──────────────────────┐   │
│                                          │  Finsus Wallet (MXN) │   │
│                                          │  ASE México          │   │
│                                          │  (Cuenta del Migrante)│  │
│                                          └─────────┬────────────┘   │
│                                                    │                │
│                                                    │ ② Cuando alcanza meta
│                                                    │                │
│                                          FASE II: MXN → MXN         │
│                                         (One-time Payment)          │
│                                                    │                │
│                                                    ▼                │
│                                          ┌──────────────────────┐   │
│                                          │ Merchant Wallet (MXN)│   │
│                                          │ ASE México           │   │
│                                          │ (Proveedor Materiales)│  │
│                                          └──────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

            ▲                                    │
            │                                    │
            └────── API REST (FastAPI) ──────────┘
                   (Orchestrates Open Payments)
```

### Componentes Principales

1. **FastAPI Backend** (`app/main.py`)
   - Orquesta los flujos de Open Payments
   - Gestiona proyectos, etapas y transacciones
   - Procesa webhooks de notificaciones de pago

2. **Open Payments Client** (`app/services/open_payments.py`)
   - Cliente HTTP para interactuar con APIs de Open Payments
   - Implementa GNAP para autorización
   - Gestiona quotes, pagos entrantes y salientes

3. **Recurring Payment Service** (`app/services/recurring_payments.py`)
   - Implementa Fase I: USD → MXN
   - Configura pagos recurrentes con monto fijo de débito
   - Actualiza progreso de ahorro

4. **One-Time Payment Service** (`app/services/one_time_payment.py`)
   - Implementa Fase II: MXN → Merchant
   - Procesa compras únicas de materiales
   - Gestiona pagos entrantes y salientes

5. **Database Models** (`app/models.py`)
   - PostgreSQL con SQLAlchemy ORM
   - Modelos: Migrant, Project, ProjectStage, RecurringPaymentSetup, MaterialPurchase, Transaction

---

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.9+**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para PostgreSQL
- **Pydantic** - Validación de datos
- **httpx/aiohttp** - Cliente HTTP asíncrono

### Base de Datos
- **PostgreSQL** - Base de datos relacional

### Protocolo de Pagos
- **Open Payments API** - Protocolo estándar para pagos
- **GNAP** - Grant Negotiation and Authorization Protocol
- **Interledger Protocol (ILP)** - Capa de liquidación subyacente

### Desarrollo
- **pytest** - Testing
- **black** - Code formatting
- **flake8** - Linting

---

## ⚙️ Configuración e Instalación

### Prerrequisitos

- Python 3.9 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)
- Acceso al sandbox de Open Payments (Rafiki)

### Instalación Paso a Paso

#### 1. Clonar el repositorio

```bash
cd constructoken-hackathon
```

#### 2. Crear y activar entorno virtual

```bash
# En macOS/Linux
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 4. Configurar la base de datos

```bash
# Crear base de datos PostgreSQL
createdb constructoken_hackathon

# O usando psql
psql -U postgres
CREATE DATABASE constructoken_hackathon;
\q
```

#### 5. Configurar variables de entorno

```bash
# Copiar archivo de plantilla
cp env.template .env

# Editar .env con tus configuraciones
nano .env  # o usa tu editor favorito
```

**📖 Para instrucciones detalladas de configuración del Test Wallet, consulta:** `SETUP_TESTNET.md`

**Variables importantes a configurar:**

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/constructoken_hackathon

# Open Payments Sandbox (Rafiki)
# Crea cuentas en: https://rafiki.money
US_WALLET_ADDRESS=https://cloud-nine-wallet-backend.akash.rafiki.money/accounts/your-us-account
US_AUTH_SERVER=https://cloud-nine-wallet-backend.akash.rafiki.money/auth
US_RESOURCE_SERVER=https://cloud-nine-wallet-backend.akash.rafiki.money

FINSUS_WALLET_ADDRESS=https://happy-life-bank-backend.akash.rafiki.money/accounts/your-finsus-account
FINSUS_AUTH_SERVER=https://happy-life-bank-backend.akash.rafiki.money/auth
FINSUS_RESOURCE_SERVER=https://happy-life-bank-backend.akash.rafiki.money

MERCHANT_WALLET_ADDRESS=https://happy-life-bank-backend.akash.rafiki.money/accounts/your-merchant-account
MERCHANT_AUTH_SERVER=https://happy-life-bank-backend.akash.rafiki.money/auth
MERCHANT_RESOURCE_SERVER=https://happy-life-bank-backend.akash.rafiki.money
```

#### 6. Inicializar la base de datos

La base de datos se inicializa automáticamente al iniciar la aplicación, pero puedes hacerlo manualmente:

```bash
python -c "from app.database import init_db; init_db()"
```

#### 7. Ejecutar la aplicación

```bash
# Modo desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O usando Python directamente
python -m app.main
```

La API estará disponible en: **http://localhost:8000**

Documentación interactiva (Swagger): **http://localhost:8000/docs**

---

## 💳 Flujos de Pago

### Fase I: Pagos Recurrentes (USD → MXN)

**Caso de uso:** "Send recurring remittances with a fixed debit amount"

#### Pasos Técnicos

1. **Request Grant (GNAP)**
   ```
   POST {US_AUTH_SERVER}/
   ```
   - El cliente solicita autorización para crear pagos recurrentes
   - Especifica: monto, frecuencia (weekly), número de pagos (10)
   - El migrante autoriza el pago
   - Respuesta: access_token + grant_id

2. **Create Quote**
   ```
   POST {US_RESOURCE_SERVER}/quotes
   ```
   - Solicita cotización para conversión USD → MXN
   - Monto de débito fijo (USD) o monto de recepción fijo (MXN)
   - Respuesta: quote_id + tasas de cambio

3. **Create Recurring Outgoing Payment**
   ```
   POST {US_RESOURCE_SERVER}/outgoing-payments
   ```
   - Instruye a la wallet USD a ejecutar pagos recurrentes
   - Utiliza quote_id obtenido
   - Los pagos se ejecutan automáticamente según la frecuencia

4. **Webhook Notifications**
   ```
   POST /webhooks/payments
   ```
   - Cada vez que un pago se completa, se recibe una notificación
   - El sistema actualiza el progreso del ahorro
   - Cuando se alcanza la meta, marca la etapa como "funded"

#### Endpoint API

```bash
POST /recurring-payments/setup
Content-Type: application/json

{
  "stage_id": 1,
  "installment_amount_mxn": 100.0,
  "number_of_payments": 10,
  "interval": "weekly"
}
```

### Fase II: Compra Única (MXN → Merchant)

**Caso de uso:** "Accept a one-time payment for an online purchase"

#### Pasos Técnicos

1. **Create Incoming Payment (Merchant)**
   ```
   POST {MERCHANT_RESOURCE_SERVER}/incoming-payments
   ```
   - El merchant crea una "factura" por $1,000 MXN
   - Respuesta: incoming_payment_id

2. **Request Grant (Buyer - Finsus)**
   ```
   POST {FINSUS_AUTH_SERVER}/
   ```
   - El comprador (migrante vía Finsus) solicita autorización
   - Para realizar un pago único de $1,000 MXN
   - Respuesta: access_token + grant_id

3. **Create Quote**
   ```
   POST {FINSUS_RESOURCE_SERVER}/quotes
   ```
   - Confirma el monto exacto a transferir
   - Incluye comisiones si las hay

4. **Create Outgoing Payment**
   ```
   POST {FINSUS_RESOURCE_SERVER}/outgoing-payments
   ```
   - Ejecuta el pago desde Finsus hacia merchant
   - Referencia el incoming_payment_id del merchant
   - Utiliza el quote_id

5. **Complete Incoming Payment**
   ```
   POST {MERCHANT_RESOURCE_SERVER}/incoming-payments/{id}/complete
   ```
   - El merchant confirma recepción de fondos
   - Verificación criptográfica (fulfillment)

6. **Webhook Notifications**
   - Notificaciones de completado o falla
   - Actualiza estado de compra en la base de datos

#### Endpoint API

```bash
POST /material-purchases
Content-Type: application/json

{
  "stage_id": 1,
  "merchant_name": "Materiales de Construcción XYZ",
  "merchant_wallet_address": "https://merchant-ase.example.com/accounts/merchant",
  "items_description": "Cemento, arena, grava para cimentación",
  "delivery_address": "Calle Principal 123, Ciudad, México",
  "delivery_notes": "Entregar en la mañana"
}
```

---

## 📡 API Endpoints

### Health Check

- `GET /` - Root endpoint
- `GET /health` - Health check

### Migrants (Usuarios Migrantes)

- `POST /migrants` - Crear nuevo migrante
- `GET /migrants/{migrant_id}` - Obtener migrante por ID
- `GET /migrants` - Listar todos los migrantes

### Projects (Proyectos de Construcción)

- `POST /projects?migrant_id={id}` - Crear nuevo proyecto con etapas
- `GET /projects/{project_id}` - Obtener proyecto con etapas
- `GET /migrants/{migrant_id}/projects` - Listar proyectos de un migrante
- `GET /stages/{stage_id}` - Obtener etapa específica

### Phase I: Recurring Payments

- `POST /recurring-payments/setup` - Configurar pagos recurrentes
- `GET /recurring-payments/{setup_id}/status` - Ver estado de pagos recurrentes
- `GET /stages/{stage_id}/funding-status` - Ver progreso de ahorro

### Phase II: Material Purchase

- `POST /material-purchases` - Comprar materiales
- `GET /material-purchases/{purchase_id}/status` - Ver estado de compra
- `GET /material-purchases?stage_id={id}` - Listar compras

### Transactions

- `GET /transactions` - Listar todas las transacciones
- `GET /transactions/{transaction_id}` - Obtener transacción específica
- `GET /transactions?stage_id={id}` - Transacciones de una etapa

### Webhooks

- `POST /webhooks/payments` - Recibir notificaciones de Open Payments

### Demo/Testing

- `POST /demo/simulate-payment-completion` - Simular completado de pago (para pruebas)

---

## 🧪 Configuración del Sandbox

### Interledger Test Wallet (Open Payments Testnet)

El [Interledger Test Wallet](https://wallet.interledger-test.dev) es una plataforma oficial para probar integraciones con Open Payments.

#### Paso 1: Crear Cuenta en Test Wallet

Visita: [https://wallet.interledger-test.dev](https://wallet.interledger-test.dev)

1. Haz clic en **"Create account"**
2. Proporciona tu email y contraseña
3. Verifica tu email
4. Completa el proceso KYC (puedes usar datos ficticios excepto el email)

#### Paso 2: Crear 3 Cuentas de Wallet

Una vez dentro del dashboard, necesitas crear **3 cuentas**:

1. **US Wallet (USD)** - Para el migrante en Estados Unidos
   - Clic en "New account"
   - Nombre: "Migrant USD"
   - Moneda: **USD**
   - Fondear con: $1,000 USD (de prueba)
   
2. **Finsus Wallet (MXN)** - Para la cuenta de ahorro en México
   - Clic en "New account"
   - Nombre: "Finsus MXN"
   - Moneda: **MXN**
   - Fondear con: $0 MXN (se irá llenando con remesas)
   
3. **Merchant Wallet (MXN)** - Para el proveedor de materiales
   - Clic en "New account"
   - Nombre: "Merchant MXN"
   - Moneda: **MXN**
   - Fondear con: $0 MXN (recibirá pagos)

#### Paso 3: Obtener Direcciones de Wallet (Payment Pointers)

Cada cuenta tendrá un **Payment Pointer** como:
```
https://ilp.interledger-test.dev/[tu-usuario]/[nombre-cuenta]
```

Ejemplo:
```
https://ilp.interledger-test.dev/juan.perez/migrant-usd
https://ilp.interledger-test.dev/juan.perez/finsus-mxn
https://ilp.interledger-test.dev/juan.perez/merchant-mxn
```

Copia estas direcciones desde el dashboard y actualiza tu archivo `.env`.

#### Paso 4: Configurar Variables de Entorno

Los servidores de auth y recursos para Interledger Test Wallet son:

```env
# US Wallet (USD)
US_WALLET_ADDRESS=https://ilp.interledger-test.dev/[tu-usuario]/migrant-usd
US_AUTH_SERVER=https://auth.interledger-test.dev
US_RESOURCE_SERVER=https://backend.interledger-test.dev

# Finsus Wallet (MXN)
FINSUS_WALLET_ADDRESS=https://ilp.interledger-test.dev/[tu-usuario]/finsus-mxn
FINSUS_AUTH_SERVER=https://auth.interledger-test.dev
FINSUS_RESOURCE_SERVER=https://backend.interledger-test.dev

# Merchant Wallet (MXN)
MERCHANT_WALLET_ADDRESS=https://ilp.interledger-test.dev/[tu-usuario]/merchant-mxn
MERCHANT_AUTH_SERVER=https://auth.interledger-test.dev
MERCHANT_RESOURCE_SERVER=https://backend.interledger-test.dev
```

**Nota**: Todos los auth y resource servers son los mismos porque están en el mismo testnet.

#### Paso 5: Fondear las Wallets

En el dashboard del Test Wallet:
1. Selecciona la cuenta
2. Haz clic en **"Deposit"**
3. Ingresa un monto entre 50 y 1,000
4. Los fondos son ficticios para pruebas

---

## 🧪 Pruebas

### Flujo Completo de Prueba

#### 1. Crear un Migrante

```bash
curl -X POST http://localhost:8000/migrants \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.perez@example.com",
    "full_name": "Juan Pérez",
    "phone": "+1-555-0123",
    "us_wallet_address": "https://cloud-nine-wallet-backend.akash.rafiki.money/accounts/juan-usd",
    "finsus_wallet_address": "https://happy-life-bank-backend.akash.rafiki.money/accounts/juan-mxn"
  }'
```

#### 2. Crear un Proyecto con Etapas

```bash
curl -X POST "http://localhost:8000/projects?migrant_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Casa Nueva",
    "description": "Construcción de vivienda familiar en Guadalajara",
    "location": "Guadalajara, Jalisco, México",
    "total_budget_mxn": 3000.0,
    "stages": [
      {
        "name": "Cimentación",
        "description": "Excavación y cimientos",
        "order": 1,
        "target_amount_mxn": 1000.0
      },
      {
        "name": "Muros y Estructura",
        "description": "Construcción de muros principales",
        "order": 2,
        "target_amount_mxn": 1000.0
      },
      {
        "name": "Techo",
        "description": "Instalación de techo",
        "order": 3,
        "target_amount_mxn": 1000.0
      }
    ]
  }'
```

#### 3. Configurar Pagos Recurrentes (Fase I)

```bash
curl -X POST http://localhost:8000/recurring-payments/setup \
  -H "Content-Type: application/json" \
  -d '{
    "stage_id": 1,
    "installment_amount_mxn": 100.0,
    "number_of_payments": 10,
    "interval": "weekly"
  }'
```

#### 4. Ver Progreso de Ahorro

```bash
curl http://localhost:8000/stages/1/funding-status
```

#### 5. Simular Pagos (Para Pruebas)

```bash
# Simular completado de cada pago recurrente
for i in {1..10}; do
  curl -X POST http://localhost:8000/demo/simulate-payment-completion \
    -H "Content-Type: application/json" \
    -d "{
      \"payment_id\": \"payment-$i\",
      \"payment_type\": \"recurring\"
    }"
  sleep 1
done
```

#### 6. Comprar Materiales (Fase II)

Una vez que la etapa esté fondeada:

```bash
curl -X POST http://localhost:8000/material-purchases \
  -H "Content-Type: application/json" \
  -d '{
    "stage_id": 1,
    "merchant_name": "Materiales de Construcción López",
    "merchant_wallet_address": "https://happy-life-bank-backend.akash.rafiki.money/accounts/merchant",
    "items_description": "Cemento (50 bultos), Arena (2 m³), Grava (2 m³)",
    "delivery_address": "Av. Revolución 456, Guadalajara, Jalisco",
    "delivery_notes": "Entregar entre 8am - 12pm"
  }'
```

#### 7. Ver Estado de Compra

```bash
curl http://localhost:8000/material-purchases/1/status
```

### Pruebas Automatizadas

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html
```

---

## 📚 Documentación Adicional

### Open Payments

- **Sitio oficial**: [https://openpayments.dev](https://openpayments.dev)
- **Getting Started**: [https://openpayments.dev/overview/getting-started/](https://openpayments.dev/overview/getting-started/)
- **GitHub**: [https://github.com/interledger/open-payments](https://github.com/interledger/open-payments)

### Interledger

- **Sitio oficial**: [https://interledger.org](https://interledger.org)
- **Hackathon**: [https://interledger.org/es/summit/hackaton](https://interledger.org/es/summit/hackaton)

### Rafiki (Sandbox)

- **Rafiki Money**: [https://rafiki.money](https://rafiki.money)
- **Rafiki GitHub**: [https://github.com/interledger/rafiki](https://github.com/interledger/rafiki)

### FastAPI

- **Documentación**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

## 🎯 Diferencias con el Proyecto Real

Este prototipo para el hackathon difiere del proyecto real de Constructoken en los siguientes aspectos:

| Aspecto | Hackathon | Proyecto Real |
|---------|-----------|---------------|
| **Frontend** | No incluido (solo API) | React con interfaz completa |
| **Autenticación** | Simplificada | JWT + OAuth2 completo |
| **Base de Datos** | Esquema básico | Esquema completo con más entidades |
| **Pagos** | Solo Open Payments | Múltiples integraciones (Stripe, etc.) |
| **Catálogo** | No incluido | Catálogo completo de materiales |
| **Entrega** | Simulada | Integración con proveedores logísticos |
| **Notificaciones** | Solo webhooks | Email, SMS, push notifications |

Este prototipo se enfoca **exclusivamente** en demostrar la integración con **Open Payments** para el caso de uso de pagos recurrentes transfronterizos y compras únicas.

---

## 🤝 Contribuciones

Este proyecto fue desarrollado para el **Interledger Hackathon 2025**.

**Autor**: [Tu Nombre]  
**Email**: [Tu Email]  
**Hackathon**: [https://interledger.org/es/summit/hackaton](https://interledger.org/es/summit/hackaton)

---

## 📄 Licencia

Este proyecto es un prototipo para el hackathon. [Especifica tu licencia aquí]

---

## 🙏 Agradecimientos

- Equipo de Interledger Foundation
- Comunidad de Open Payments
- Equipo de Rafiki por el sandbox

---

## 📞 Soporte

Para preguntas sobre este prototipo:

- **Issues**: [GitHub Issues]
- **Email**: [tu-email@example.com]
- **Slack del Hackathon**: [Canal específico]

---

**¡Construyendo el futuro de los pagos transfronterizos! 🚀🏗️**

