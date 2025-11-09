# 🏗️ Arquitectura Técnica - Constructoken Hackathon

## Diagrama de Arquitectura General

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                         CONSTRUCTOKEN ECOSYSTEM                             │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│   MIGRANT (USA)     │
│  Usuario Final      │
└──────┬──────────────┘
       │
       │ HTTP Requests (REST API)
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                                    │
│                     (Orchestration Layer)                                 │
│                                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐                 │
│  │   main.py   │  │ Recurring    │  │  One-Time      │                 │
│  │  (Endpoints)│─▶│ Payment      │  │  Payment       │                 │
│  │             │  │ Service      │  │  Service       │                 │
│  └─────────────┘  └──────┬───────┘  └────────┬───────┘                 │
│                           │                    │                         │
│                           └──────┬─────────────┘                         │
│                                  │                                       │
│                                  ▼                                       │
│                    ┌─────────────────────────┐                          │
│                    │  Open Payments Client   │                          │
│                    │  (API Integration)      │                          │
│                    └──────────┬──────────────┘                          │
│                               │                                          │
└───────────────────────────────┼──────────────────────────────────────────┘
                                │
                                │ GNAP + Open Payments API
                                │
        ┌───────────────────────┼──────────────────────────┐
        │                       │                          │
        ▼                       ▼                          ▼
┌───────────────┐      ┌────────────────┐       ┌──────────────────┐
│  US ASE       │      │  FINSUS ASE    │       │  MERCHANT ASE    │
│  (USD Wallet) │      │  (MXN Wallet)  │       │  (MXN Wallet)    │
│               │      │                │       │                  │
│ Auth Server   │      │  Auth Server   │       │  Auth Server     │
│ Resource      │      │  Resource      │       │  Resource        │
│ Server        │      │  Server        │       │  Server          │
└───────────────┘      └────────────────┘       └──────────────────┘
        │                       │                          │
        │                       │                          │
        └─────── ILP (Interledger Protocol) ──────────────┘
                 (Settlement Layer)


┌──────────────────────────────────────────────────────────────────────────┐
│                        POSTGRESQL DATABASE                                │
│                                                                           │
│  ┌──────────┐  ┌─────────┐  ┌──────────────┐  ┌─────────────┐         │
│  │ Migrants │  │ Projects│  │ ProjectStages│  │ Transactions│         │
│  └──────────┘  └─────────┘  └──────────────┘  └─────────────┘         │
│                                                                           │
│  ┌──────────────────────┐   ┌─────────────────────┐                    │
│  │ RecurringPaymentSetup│   │ MaterialPurchases   │                    │
│  └──────────────────────┘   └─────────────────────┘                    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Datos: Fase I (Recurring Payments)

```
┌──────────────────────────────────────────────────────────────────────────┐
│           FASE I: PAGOS RECURRENTES USD → MXN                            │
│        "Send recurring remittances with a fixed debit amount"            │
└──────────────────────────────────────────────────────────────────────────┘

Step 1: GRANT NEGOTIATION (GNAP)
┌──────────────┐                                      ┌─────────────────┐
│   Cliente    │  POST /grants/request                │  US Auth Server │
│ (Constructoken)├────────────────────────────────────▶│                 │
│              │                                       │  (GNAP)         │
│              │  ◀─────────────────────────────────── │                 │
│              │  access_token + grant_id              └─────────────────┘
└──────────────┘

Step 2: CREATE QUOTE
┌──────────────┐                                      ┌──────────────────┐
│   Cliente    │  POST /quotes                        │ US Resource      │
│              │  {                                   │ Server           │
│              │    walletAddress: US_WALLET,         │                  │
│              │    receiver: FINSUS_WALLET,          │                  │
│              │    receiveAmount: {                  │                  │
│              │      value: "10000", // 100 MXN      │                  │
│              │      assetCode: "MXN",               │                  │
│              │      assetScale: 2                   │                  │
│              │    }                                 │                  │
│              │  }                                   │                  │
│              ├─────────────────────────────────────▶│                  │
│              │                                      │                  │
│              │  ◀────────────────────────────────── │                  │
│              │  quote_id + exchange rate            └──────────────────┘
└──────────────┘

Step 3: CREATE RECURRING OUTGOING PAYMENT
┌──────────────┐                                      ┌──────────────────┐
│   Cliente    │  POST /outgoing-payments             │ US Resource      │
│              │  {                                   │ Server           │
│              │    walletAddress: US_WALLET,         │                  │
│              │    quoteId: quote_id,                │                  │
│              │    metadata: {                       │                  │
│              │      description: "Recurring for     │                  │
│              │                    stage 1",         │                  │
│              │      interval: "weekly",             │                  │
│              │      iterations: 10                  │                  │
│              │    }                                 │                  │
│              │  }                                   │                  │
│              ├─────────────────────────────────────▶│                  │
│              │                                      │                  │
│              │  ◀────────────────────────────────── │                  │
│              │  outgoing_payment_id                 └──────────────────┘
└──────────────┘

Step 4: AUTOMATIC PAYMENT EXECUTION (Weekly)
┌──────────────┐                  ILP                 ┌──────────────────┐
│  US ASE      │ ═══════════════════════════════════▶ │  FINSUS ASE      │
│  (USD)       │  Transfer funds                      │  (MXN)           │
└──────────────┘  (10 times, weekly)                  └──────────────────┘
       │                                                       │
       │                                                       │
       ▼                                                       ▼
   WEBHOOK                                               WEBHOOK
outgoing_payment.completed                         incoming_payment.completed

       │                                                       │
       └───────────────────────┬───────────────────────────────┘
                               │
                               ▼
                   ┌────────────────────────┐
                   │  Constructoken Backend │
                   │  POST /webhooks/payments│
                   │                        │
                   │  Updates:              │
                   │  - Stage amount        │
                   │  - Transaction record  │
                   │  - Funding status      │
                   └────────────────────────┘
```

---

## Flujo de Datos: Fase II (One-Time Purchase)

```
┌──────────────────────────────────────────────────────────────────────────┐
│           FASE II: COMPRA ÚNICA MXN → MERCHANT                           │
│       "Accept a one-time payment for an online purchase"                 │
└──────────────────────────────────────────────────────────────────────────┘

Step 1: CREATE INCOMING PAYMENT (Merchant Side)
┌──────────────┐                                      ┌──────────────────┐
│   Merchant   │  POST /incoming-payments             │ Merchant         │
│   Client     │  {                                   │ Resource Server  │
│(Constructoken)│    walletAddress: MERCHANT_WALLET,  │                  │
│              │    incomingAmount: {                 │                  │
│              │      value: "100000", // 1000 MXN    │                  │
│              │      assetCode: "MXN",               │                  │
│              │      assetScale: 2                   │                  │
│              │    }                                 │                  │
│              │  }                                   │                  │
│              ├─────────────────────────────────────▶│                  │
│              │  ◀────────────────────────────────── │                  │
│              │  incoming_payment_id                 └──────────────────┘
└──────────────┘

Step 2: REQUEST GRANT (Buyer/Finsus Side)
┌──────────────┐                                      ┌─────────────────┐
│   Cliente    │  POST /grants/request                │ Finsus Auth     │
│ (Constructoken)├────────────────────────────────────▶│ Server          │
│              │  ◀─────────────────────────────────── │                 │
│              │  access_token + grant_id             └─────────────────┘
└──────────────┘

Step 3: CREATE QUOTE
┌──────────────┐                                      ┌──────────────────┐
│   Cliente    │  POST /quotes                        │ Finsus Resource  │
│              │  {                                   │ Server           │
│              │    walletAddress: FINSUS_WALLET,     │                  │
│              │    receiver: MERCHANT_WALLET,        │                  │
│              │    receiveAmount: {                  │                  │
│              │      value: "100000", // 1000 MXN    │                  │
│              │      assetCode: "MXN",               │                  │
│              │      assetScale: 2                   │                  │
│              │    }                                 │                  │
│              │  }                                   │                  │
│              ├─────────────────────────────────────▶│                  │
│              │  ◀────────────────────────────────── │                  │
│              │  quote_id                            └──────────────────┘
└──────────────┘

Step 4: CREATE OUTGOING PAYMENT (Buyer Side)
┌──────────────┐                                      ┌──────────────────┐
│   Cliente    │  POST /outgoing-payments             │ Finsus Resource  │
│              │  {                                   │ Server           │
│              │    walletAddress: FINSUS_WALLET,     │                  │
│              │    quoteId: quote_id,                │                  │
│              │    metadata: {                       │                  │
│              │      incomingPaymentId:              │                  │
│              │        incoming_payment_id           │                  │
│              │    }                                 │                  │
│              │  }                                   │                  │
│              ├─────────────────────────────────────▶│                  │
│              │  ◀────────────────────────────────── │                  │
│              │  outgoing_payment_id                 └──────────────────┘
└──────────────┘

Step 5: PAYMENT EXECUTION
┌──────────────┐                  ILP                 ┌──────────────────┐
│ FINSUS ASE   │ ═══════════════════════════════════▶ │  MERCHANT ASE    │
│  (MXN)       │  Transfer 1000 MXN                   │  (MXN)           │
└──────────────┘                                      └──────────────────┘
       │                                                       │
       │                                                       │
       ▼                                                       ▼
   WEBHOOK                                               WEBHOOK
outgoing_payment.completed                         incoming_payment.completed

Step 6: COMPLETE INCOMING PAYMENT
                                                      ┌──────────────────┐
                                                      │ Merchant         │
                                                      │ Resource Server  │
                                                      │                  │
                                 POST /incoming-      │  Cryptographic   │
                                 payments/{id}/       │  fulfillment     │
                                 complete             │  verification    │
                                                      │                  │
                                                      └──────────────────┘
```

---

## Estructura de Base de Datos

```sql
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                              │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│    migrants      │
├──────────────────┤
│ id (PK)          │
│ email            │◀─────────┐
│ full_name        │          │
│ phone            │          │
│ us_wallet_address│          │ 1:N
│ finsus_wallet_   │          │
│   address        │          │
│ created_at       │          │
└──────────────────┘          │
                              │
                     ┌────────┴────────┐
                     │    projects     │
                     ├─────────────────┤
                     │ id (PK)         │
                     │ migrant_id (FK) │
                     │ name            │◀──────┐
                     │ description     │       │
                     │ location        │       │
                     │ total_budget_mxn│       │ 1:N
                     │ status          │       │
                     │ created_at      │       │
                     └─────────────────┘       │
                                               │
                                      ┌────────┴──────────┐
                                      │  project_stages   │
                                      ├───────────────────┤
                                      │ id (PK)           │
                                      │ project_id (FK)   │
                                      │ name              │
                                      │ description       │
                                      │ order             │
                                      │ target_amount_mxn │
                                      │ current_amount_mxn│
                                      │ is_funded         │
                                      │ is_purchased      │
                                      │ created_at        │
                                      │ funded_at         │
                                      └───────────────────┘
                                               │
                        ┌──────────────────────┼──────────────────────┐
                        │                      │                      │
                        │ 1:1                  │ 1:N                  │ 1:1
                        │                      │                      │
            ┌───────────▼──────────┐  ┌────────▼────────┐  ┌─────────▼────────┐
            │ recurring_payment_   │  │  transactions   │  │ material_        │
            │ setups               │  ├─────────────────┤  │ purchases        │
            ├──────────────────────┤  │ id (PK)         │  ├──────────────────┤
            │ id (PK)              │  │ stage_id (FK)   │  │ id (PK)          │
            │ stage_id (FK)        │  │ payment_type    │  │ stage_id (FK)    │
            │ grant_id             │  │ amount_mxn      │  │ merchant_name    │
            │ access_token         │  │ amount_usd      │  │ items_description│
            │ total_amount_mxn     │  │ sender_wallet_  │  │ total_amount_mxn │
            │ installment_amount_  │  │   address       │  │ buyer_wallet_    │
            │   mxn                │  │ recipient_wallet│  │   address        │
            │ number_of_payments   │  │   _address      │  │ merchant_wallet_ │
            │ interval             │  │ quote_id        │  │   address        │
            │ sender_wallet_       │  │ outgoing_payment│  │ incoming_payment │
            │   address            │  │   _id           │  │   _id            │
            │ recipient_wallet_    │  │ incoming_payment│  │ quote_id         │
            │   address            │  │   _id           │  │ outgoing_payment │
            │ quote_id             │  │ status          │  │   _id            │
            │ outgoing_payment_id  │  │ error_message   │  │ grant_id         │
            │ is_active            │  │ created_at      │  │ status           │
            │ payments_completed   │  │ completed_at    │  │ delivery_address │
            │ created_at           │  └─────────────────┘  │ delivery_notes   │
            │ completed_at         │                       │ created_at       │
            └──────────────────────┘                       │ completed_at     │
                                                           └──────────────────┘
```

---

## Componentes de Software

### 1. API Layer (`app/main.py`)

**Responsabilidades:**
- Exponer endpoints REST
- Validación de requests con Pydantic
- Manejo de errores y excepciones
- Procesamiento de webhooks
- Documentación automática (Swagger/OpenAPI)

**Endpoints principales:**
- `/migrants` - CRUD de migrantes
- `/projects` - Gestión de proyectos
- `/recurring-payments/setup` - Configurar pagos recurrentes
- `/material-purchases` - Comprar materiales
- `/webhooks/payments` - Recibir notificaciones

### 2. Service Layer

#### a) `open_payments.py` - Cliente de Open Payments

**Responsabilidades:**
- HTTP client para APIs de Open Payments
- Implementación de GNAP (Grant Negotiation)
- Gestión de access tokens
- Operaciones CRUD para:
  - Grants
  - Quotes
  - Outgoing Payments
  - Incoming Payments
  - Wallet Addresses

**Métodos clave:**
- `request_grant()` - Solicitar autorización
- `create_quote()` - Crear cotización
- `create_outgoing_payment()` - Crear pago saliente
- `create_incoming_payment()` - Crear pago entrante
- `get_wallet_address_info()` - Obtener info de wallet

#### b) `recurring_payments.py` - Servicio de Pagos Recurrentes

**Responsabilidades:**
- Orquestar Fase I (USD → MXN)
- Configurar serie de pagos recurrentes
- Procesar webhooks de pagos recurrentes
- Actualizar progreso de ahorro
- Marcar etapas como fondeadas

**Métodos clave:**
- `setup_recurring_payment()` - Configurar pagos
- `process_recurring_payment_webhook()` - Procesar notificaciones
- `check_payment_status()` - Verificar estado

#### c) `one_time_payment.py` - Servicio de Pago Único

**Responsabilidades:**
- Orquestar Fase II (MXN → Merchant)
- Crear incoming payment en merchant
- Ejecutar outgoing payment desde Finsus
- Completar transacción
- Actualizar estado de compra

**Métodos clave:**
- `create_material_purchase()` - Crear compra
- `process_purchase_webhook()` - Procesar notificaciones
- `check_purchase_status()` - Verificar estado

### 3. Data Layer

#### `database.py`
- Configuración de SQLAlchemy
- Session management
- Connection pooling

#### `models.py`
- Definición de tablas ORM
- Relaciones entre entidades
- Enums de estado

#### `schemas/payment_schemas.py`
- Validación con Pydantic
- Serialización/Deserialización
- Documentación de tipos

### 4. Configuration Layer

#### `config.py`
- Carga de variables de entorno
- Settings centralizados
- Validación de configuración

---

## Seguridad

### Autenticación y Autorización

1. **GNAP (Grant Negotiation and Authorization Protocol)**
   - Reemplaza OAuth 2.0 en Open Payments
   - Grants con permisos granulares
   - Tokens de acceso con tiempo de vida limitado
   - Interacción de usuario para autorización

2. **Access Tokens**
   - Almacenados temporalmente
   - Expiración automática
   - Renovación mediante continuation

3. **Wallet Addresses**
   - Públicamente descubribles (como emails)
   - No exponen información sensible
   - Solo metadatos del endpoint

### Validación de Pagos

1. **Cryptographic Fulfillment**
   - ILP utiliza firma criptográfica
   - Verificación de recepción de fondos
   - Prevención de doble gasto

2. **Quote Validation**
   - Cotizaciones con expiración
   - Validación de montos antes de ejecutar
   - Prevención de cambios de precio

### Datos Sensibles

- Access tokens en base de datos (considerar encriptación)
- Información personal de migrantes
- Detalles de transacciones financieras

**Recomendaciones para producción:**
- Encriptar campos sensibles
- Implementar HTTPS obligatorio
- Rate limiting en endpoints públicos
- Logging de auditoría

---

## Escalabilidad

### Consideraciones

1. **Asynchronous Processing**
   - Uso de `async/await` en Python
   - Background tasks para webhooks
   - No bloquear la respuesta HTTP

2. **Database Optimization**
   - Índices en campos frecuentemente consultados
   - Connection pooling configurado
   - Queries optimizadas con eager loading

3. **Caching**
   - Access tokens cacheados
   - Información de wallet addresses

4. **Horizontal Scaling**
   - Stateless API (puede escalar horizontalmente)
   - Load balancer entre instancias
   - Shared database o replicación

### Mejoras Futuras

- **Message Queue**: Para procesar webhooks (RabbitMQ, Celery)
- **Redis**: Para caching y sesiones
- **CDN**: Para assets estáticos (frontend futuro)
- **Microservicios**: Separar lógica de pagos recurrentes y compras

---

## Monitoreo y Observabilidad

### Logging

- Logs estructurados con `logging` de Python
- Niveles: INFO, WARNING, ERROR
- Logs de todas las llamadas a Open Payments API
- Logs de webhooks recibidos

### Métricas (Futuro)

- Número de transacciones por minuto
- Tiempo de respuesta de APIs
- Tasa de éxito/falla de pagos
- Latencia de Open Payments APIs

### Alertas (Futuro)

- Pagos fallidos consecutivos
- Webhooks no procesados
- Errores de autorización
- Database connection issues

---

## Testing

### Estrategia de Pruebas

1. **Unit Tests**
   - Probar funciones individuales
   - Mocks para Open Payments API
   - Coverage > 80%

2. **Integration Tests**
   - Probar flujos completos
   - Usar sandbox de Rafiki
   - Simular webhooks

3. **End-to-End Tests**
   - Flujo completo: Creación → Fondeo → Compra
   - Usar datos de prueba
   - Verificar estado final en DB

### Herramientas

- **pytest**: Framework de testing
- **pytest-asyncio**: Tests async
- **httpx MockTransport**: Mock de HTTP calls
- **SQLAlchemy TestSession**: Tests de DB

---

## Deployment

### Ambientes

1. **Development**: Local con `.env`
2. **Staging**: Sandbox de Rafiki
3. **Production**: ASEs reales (futuro)

### Requisitos de Infraestructura

- **Compute**: 1 CPU, 2GB RAM (mínimo)
- **Database**: PostgreSQL 12+
- **Network**: HTTPS con certificado válido
- **Storage**: Minimal (solo DB)

### Opciones de Deploy

1. **Heroku**: Fácil, ideal para hackathon
2. **AWS ECS/Fargate**: Containerizado
3. **Digital Ocean**: VPS simple
4. **Railway**: Alternativa moderna a Heroku

---

## Limitaciones Conocidas

1. **Sandbox**: Rafiki es para pruebas, no producción
2. **Error Handling**: Básico, mejorar para producción
3. **Retry Logic**: No implementado para fallos de API
4. **Idempotencia**: Webhooks pueden duplicarse
5. **Authentication**: Simplificada para el hackathon
6. **Rate Limiting**: No implementado

---

## Roadmap Post-Hackathon

### Corto Plazo (1-3 meses)
- [ ] Frontend en React
- [ ] Autenticación completa (JWT)
- [ ] Tests automatizados completos
- [ ] Retry logic y circuit breakers
- [ ] Logging estructurado avanzado

### Mediano Plazo (3-6 meses)
- [ ] Integración con ASEs reales (no sandbox)
- [ ] Catálogo de materiales
- [ ] Sistema de notificaciones (email/SMS)
- [ ] Dashboard para migrantes
- [ ] Portal para merchants

### Largo Plazo (6-12 meses)
- [ ] App móvil (React Native)
- [ ] Integración con proveedores logísticos
- [ ] Scoring crediticio
- [ ] Marketplace completo
- [ ] Expansión a otros países

---

**Desarrollado para Interledger Hackathon 2025** 🚀

