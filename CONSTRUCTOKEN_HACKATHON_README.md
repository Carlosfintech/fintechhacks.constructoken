# Constructoken - Interledger Hackathon Prototype

## Proyecto: Constructoken

**Visión:** Un marketplace que ayuda a migrantes a financiar y autoconstruir sus viviendas en México mediante el protocolo Interledger y Open Payments.

Este prototipo demuestra dos flujos de pago fundamentales:

1. **Fase I: Remesas Recurrentes** - El migrante envía pagos semanales desde su wallet USD a su cuenta FINSUS en MXN
2. **Fase II: Compra Única** - El migrante usa los fondos acumulados para comprar materiales de construcción

---

## 📋 Tabla de Contenidos

- [Arquitectura del Flujo](#arquitectura-del-flujo)
- [Configuración del Proyecto](#configuración-del-proyecto)
- [Wallets de Prueba](#wallets-de-prueba)
- [Fase I: Remesas Recurrentes](#fase-i-remesas-recurrentes)
- [Fase II: Compra Única](#fase-ii-compra-única)
- [Endpoints de la API](#endpoints-de-la-api)
- [Pruebas Paso a Paso](#pruebas-paso-a-paso)
- [Arquitectura Técnica](#arquitectura-técnica)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura del Flujo

### Flujo General de Open Payments

Este prototipo implementa el flujo completo de autorización interactiva de Open Payments:

1. **Solicitar Grant** (incoming-payment, quote, o outgoing-payment)
2. **Crear Recursos** (IncomingPayment, Quote)
3. **Solicitar Grant Interactivo** con `interact.redirect`
4. **Redirigir al Usuario** a la URL de autorización
5. **Recibir Callback** con `interact_ref` y `hash`
6. **Validar Hash** para verificar integridad
7. **Solicitar Continuación** del grant (POST a `continue_uri`)
8. **Crear OutgoingPayment** con el nuevo token

### Fase I: Pagos Recurrentes

```
Migrante (USD) --weekly--> FINSUS (MXN)
$10 USD x 10 semanas = $100 USD → ~$1,000 MXN
```

**Características:**
- Grant con límites (`limits`) para pagos recurrentes
- Debit amount fijo: $10 USD por pago
- Intervalo: semanal (configurable)
- Cap total: $100 USD (10 pagos)
- Quote dinámico para obtener tasa de cambio actual

### Fase II: Compra Única

```
FINSUS (MXN) --one-time--> Merchant (MXN)
$1,000 MXN para materiales de construcción
```

**Características:**
- Grant interactivo para pago único
- Monto exacto de la compra
- Flujo completo de autorización con redirect

---

## ⚙️ Configuración del Proyecto

### Prerrequisitos

- Python 3.12+
- Docker & Docker Compose
- Node.js 22+ (para frontend, opcional)

### Variables de Entorno

El archivo `backend/app/app/core/config.py` ya contiene las credenciales configuradas para las 3 wallets de prueba. **No necesitas agregar nada al `.env`** para las wallets, pero asegúrate de tener las variables básicas:

```env
# .env (en la raíz del proyecto)
PROJECT_NAME=Constructoken
SERVER_NAME=localhost
DOMAIN=localhost

# Database
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis
POSTGRES_DB=app

# Redis
REDIS_PASSWORD=changethis

# Email (para desarrollo local con MailCatcher)
SMTP_HOST=mailcatcher
SMTP_PORT=1025
SMTP_TLS=false
EMAILS_FROM_EMAIL=noreply@constructoken.com

# Admin
FIRST_ADMIN=admin@constructoken.com
FIRST_ADMIN_PASSWORD=changethis

# Open Payments
DEFAULT_REDIRECT_AFTER_AUTH=http://localhost:3000/fulfil/
```

### Iniciar el Proyecto

```bash
# 1. Construir los contenedores
docker compose build --no-cache

# 2. Iniciar servicios
docker compose up -d

# 3. Verificar que el backend está corriendo
curl http://localhost/v1/payments/health
# Respuesta esperada: {"status":"ok","service":"constructoken-payments"}
```

### URLs de Desarrollo

- **Backend API:** http://localhost
- **API Docs (Swagger):** http://localhost/docs
- **API Docs (ReDoc):** http://localhost/redoc
- **Frontend:** http://localhost:3000 (si se ejecuta)

---

## 💳 Wallets de Prueba

### 1. Migrante (Pancho) - USD

**Rol:** Remitente en Fase I
- **Wallet Address:** `https://ilp.interledger-test.dev/pancho`
- **Asset:** USD, Scale: 2
- **Key ID:** `194018ce-1d8d-4ecd-b405-e564002d2c83`

### 2. FINSUS (Destinatario) - MXN

**Rol:** Receptor en Fase I, Pagador en Fase II
- **Wallet Address:** `https://ilp.interledger-test.dev/destinatario`
- **Asset:** MXN, Scale: 2
- **Key ID:** `cbb4e478-26df-4eeb-9c35-3b39a77f8ce7`

### 3. Merchant (Materiales) - MXN

**Rol:** Receptor en Fase II
- **Wallet Address:** `https://ilp.interledger-test.dev/merchant`
- **Asset:** MXN, Scale: 2
- **Key ID:** `736d4945-29ab-4a81-a566-be246bfb827d`

---

## 🔄 Fase I: Remesas Recurrentes

### Objetivo

Configurar un grant de pago recurrente que permita al migrante enviar $10 USD semanalmente desde su wallet a FINSUS, hasta acumular $100 USD (~$1,000 MXN).

### Paso 1: Iniciar el Flujo de Autorización

```bash
curl -X POST http://localhost/v1/payments/recurring/start \
  -H "Content-Type: application/json" \
  -d '{
    "debit_amount": "1000",
    "total_cap": "10000",
    "interval": "R/2025-01-01T00:00:00Z/P1W",
    "max_payments": 10
  }'
```

**Parámetros:**
- `debit_amount`: "1000" = $10.00 USD (en centavos)
- `total_cap`: "10000" = $100.00 USD total
- `interval`: ISO 8601 repeating interval (weekly)
- `max_payments`: 10 pagos

**Respuesta:**
```json
{
  "redirect_url": "https://ilp.interledger-test.dev/interact/...",
  "grant_id": "01HQXYZ..."
}
```

### Paso 2: Autorizar en el Wallet

1. **Copia la `redirect_url`** de la respuesta
2. **Abre la URL en tu navegador**
3. **Autoriza el pago** en la interfaz de Interledger Test Wallet
4. **Serás redirigido** a `http://localhost:3000/fulfil/recurring/{grant_id}?interact_ref=...&hash=...`

### Paso 3: Completar la Autorización (Automático)

El callback procesará automáticamente:
- Validación del hash
- Continuación del grant
- Almacenamiento del token de acceso

Si estás probando sin frontend, puedes simular el callback manualmente:

```bash
curl "http://localhost/v1/payments/recurring/callback?interact_ref={INTERACT_REF}&hash={HASH}&grant_id={GRANT_ID}"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Recurring payment grant established successfully...",
  "grant_id": "01HQXYZ..."
}
```

### Paso 4: Ejecutar Pagos Recurrentes

Una vez autorizado, puedes ejecutar pagos individuales:

```bash
curl -X POST http://localhost/v1/payments/recurring/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "grant_id": "01HQXYZ..."
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Recurring payment executed successfully",
  "outgoing_payment_id": "https://ilp.interledger-test.dev/...",
  "quote_debit_amount": "1000 USD",
  "quote_receive_amount": "10000 MXN",
  "payments_made": 1,
  "payments_remaining": 9
}
```

**Ejecuta este endpoint 10 veces** para simular los 10 pagos semanales.

---

## 🛒 Fase II: Compra Única

### Objetivo

Usar los fondos acumulados en FINSUS ($1,000 MXN) para comprar materiales de construcción del Merchant.

### Paso 1: Iniciar el Flujo de Compra

```bash
curl -X POST http://localhost/v1/payments/purchase/start \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "100000"
  }'
```

**Parámetros:**
- `amount`: "100000" = $1,000.00 MXN (en centavos)

**Respuesta:**
```json
{
  "redirect_url": "https://ilp.interledger-test.dev/interact/...",
  "transaction_id": "01HQABC..."
}
```

### Paso 2: Autorizar la Compra

1. **Copia la `redirect_url`**
2. **Abre la URL en tu navegador**
3. **Autoriza el pago** en la interfaz del wallet de FINSUS
4. **Serás redirigido** a `http://localhost:3000/fulfil/purchase/{transaction_id}?interact_ref=...&hash=...`

### Paso 3: Completar la Compra (Automático)

El callback procesará:
- Validación del hash
- Continuación del grant
- Creación del OutgoingPayment
- Transferencia de fondos de FINSUS a Merchant

Si pruebas sin frontend:

```bash
curl "http://localhost/v1/payments/purchase/callback?interact_ref={INTERACT_REF}&hash={HASH}&transaction_id={TRANSACTION_ID}"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Purchase completed successfully",
  "transaction_id": "01HQABC...",
  "outgoing_payment_id": "https://ilp.interledger-test.dev/..."
}
```

---

## 📡 Endpoints de la API

### Fase I: Recurring Payments

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/v1/payments/recurring/start` | Inicia el flujo de autorización |
| GET | `/v1/payments/recurring/callback` | Callback después de autorización |
| POST | `/v1/payments/recurring/trigger` | Ejecuta un pago recurrente |

### Fase II: One-Time Purchase

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/v1/payments/purchase/start` | Inicia el flujo de compra |
| GET | `/v1/payments/purchase/callback` | Callback después de autorización |

### Utilidades

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/v1/payments/health` | Health check del servicio |

---

## 🧪 Pruebas Paso a Paso

### Flujo Completo (Fase I + Fase II)

#### 1. Configurar Grant Recurrente

```bash
# Iniciar
RECURRING_RESPONSE=$(curl -s -X POST http://localhost/v1/payments/recurring/start \
  -H "Content-Type: application/json" \
  -d '{
    "debit_amount": "1000",
    "total_cap": "10000",
    "interval": "R/2025-01-01T00:00:00Z/P1W",
    "max_payments": 10
  }')

echo $RECURRING_RESPONSE | jq .

# Extraer redirect_url y grant_id
REDIRECT_URL=$(echo $RECURRING_RESPONSE | jq -r '.redirect_url')
GRANT_ID=$(echo $RECURRING_RESPONSE | jq -r '.grant_id')

echo "Visita: $REDIRECT_URL"
```

#### 2. Autorizar y Ejecutar Pagos

```bash
# Después de autorizar en el navegador y obtener interact_ref/hash del callback
# Ejecutar 10 pagos
for i in {1..10}; do
  echo "Ejecutando pago #$i..."
  curl -X POST http://localhost/v1/payments/recurring/trigger \
    -H "Content-Type: application/json" \
    -d "{\"grant_id\": \"$GRANT_ID\"}" | jq .
  sleep 2
done
```

#### 3. Realizar Compra

```bash
# Iniciar compra
PURCHASE_RESPONSE=$(curl -s -X POST http://localhost/v1/payments/purchase/start \
  -H "Content-Type: application/json" \
  -d '{"amount": "100000"}')

echo $PURCHASE_RESPONSE | jq .

# Extraer redirect_url
PURCHASE_REDIRECT=$(echo $PURCHASE_RESPONSE | jq -r '.redirect_url')
echo "Visita: $PURCHASE_REDIRECT"

# El callback completará automáticamente la compra
```

---

## 🏛️ Arquitectura Técnica

### Estructura de Archivos

```
backend/app/app/
├── api/
│   └── api_v1/
│       └── endpoints/
│           └── payments.py          # 🆕 Endpoints FastAPI
├── core/
│   └── config.py                    # ✏️ Configuración con wallets
├── schemas/
│   ├── payments.py                  # 🆕 Schemas Pydantic
│   └── openpayments/
│       └── open_payments.py         # Schemas base (reutilizados)
├── services/
│   └── open_payments_service.py     # 🆕 Lógica de negocio
├── utils/
│   └── open_payments_client.py      # 🆕 SDK helpers
├── utilities/
│   └── openpayments.py              # PaymentsParser (hop-sauna)
└── open_payments_sdk/               # SDK de Open Payments
```

### Flujo de Datos

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────────┐
│  API Call   │─────▶│  Endpoint    │─────▶│  Service Layer      │
│  (Client)   │      │  (payments)  │      │  (OpenPayments)     │
└─────────────┘      └──────────────┘      └─────────────────────┘
                                                      │
                                                      ▼
                              ┌──────────────────────────────────────┐
                              │  Open Payments SDK                    │
                              │  - HttpClient                         │
                              │  - OpenPaymentsClient                 │
                              │  - Grants, Quotes, IncomingPayments   │
                              └──────────────────────────────────────┘
                                                      │
                                                      ▼
                              ┌──────────────────────────────────────┐
                              │  Interledger Test Network             │
                              │  - Wallet Migrante (USD)              │
                              │  - Wallet FINSUS (MXN)                │
                              │  - Wallet Merchant (MXN)              │
                              └──────────────────────────────────────┘
```

### Almacenamiento en Memoria

Para el prototipo del hackathon, se usan diccionarios en memoria:

```python
# En services/open_payments_service.py
pending_recurring_grants: Dict[str, Dict] = {}
active_recurring_grants: Dict[str, RecurringPaymentGrant] = {}
pending_purchase_transactions: Dict[str, PendingIncomingPaymentTransaction] = {}
```

**⚠️ Producción:** Reemplazar con PostgreSQL/Redis.

### Validación de Hash

Implementado siguiendo la especificación de Open Payments:

```python
data = f"{incoming_payment_id}\n{finish_id}\n{interact_ref}\n{auth_server_url}".encode("utf-8")
calculated_hash = b64encode(sha256(data).digest())
```

---

## 🐛 Troubleshooting

### Error: "Grant not found in pending grants"

**Causa:** El grant ID no existe en memoria.

**Solución:**
1. Verifica que completaste el paso 1 (start)
2. Usa el `grant_id` correcto de la respuesta
3. En producción, implementar almacenamiento persistente

### Error: "Hash validation failed"

**Causa:** El hash recibido no coincide con el calculado.

**Solución:**
1. Verifica que estás usando el `interact_ref` y `hash` correctos del callback
2. No modifiques la URL de redirección
3. Asegúrate de que el `nonce` coincide con el ID de la transacción

### Error: "Maximum payments reached"

**Causa:** Ya ejecutaste los 10 pagos del grant.

**Solución:**
1. Crea un nuevo grant con `/recurring/start`
2. Ajusta `max_payments` si necesitas más

### Error: "Failed to create quote"

**Causa:** Problemas de conectividad con el wallet o credenciales incorrectas.

**Solución:**
1. Verifica que las wallets están activas en https://ilp.interledger-test.dev
2. Confirma que las credenciales en `config.py` son correctas
3. Revisa los logs del contenedor: `docker compose logs -f backend`

### El callback no se ejecuta automáticamente

**Solución:**
1. Si no tienes frontend, usa el endpoint de callback manualmente
2. Extrae `interact_ref` y `hash` de la URL de redirección
3. Llama a `/recurring/callback` o `/purchase/callback` con esos parámetros

---

## 📚 Referencias

- [Open Payments Documentation](https://openpayments.dev/)
- [Interledger Protocol](https://interledger.org/)
- [Open Payments Flow](https://openpayments.dev/concepts/op-flow/)
- [Hash Verification](https://openpayments.dev/identity/hash-verification/)
- [Hop Sauna Repository](https://codeberg.org/whythawk/hop-sauna)

---

## 🎯 Demo para el Hackathon

### Script de Demostración

```bash
#!/bin/bash

echo "🏗️  CONSTRUCTOKEN - Interledger Hackathon Demo"
echo "================================================"
echo ""

# FASE I: Remesas Recurrentes
echo "📤 FASE I: Configurando remesas recurrentes..."
GRANT_RESP=$(curl -s -X POST http://localhost/v1/payments/recurring/start \
  -H "Content-Type: application/json" \
  -d '{
    "debit_amount": "1000",
    "total_cap": "10000",
    "interval": "R/2025-01-01T00:00:00Z/P1W",
    "max_payments": 10
  }')

GRANT_ID=$(echo $GRANT_RESP | jq -r '.grant_id')
REDIRECT=$(echo $GRANT_RESP | jq -r '.redirect_url')

echo "✅ Grant creado: $GRANT_ID"
echo "🔗 Autoriza aquí: $REDIRECT"
echo ""
read -p "Presiona Enter después de autorizar..."

echo "💸 Ejecutando 10 pagos semanales..."
for i in {1..10}; do
  PAYMENT=$(curl -s -X POST http://localhost/v1/payments/recurring/trigger \
    -H "Content-Type: application/json" \
    -d "{\"grant_id\": \"$GRANT_ID\"}")

  REMAINING=$(echo $PAYMENT | jq -r '.payments_remaining')
  echo "  ✓ Pago $i/10 completado. Restantes: $REMAINING"
  sleep 1
done

echo ""
echo "✅ ¡Fase I completada! $1,000 MXN acumulados en FINSUS"
echo ""

# FASE II: Compra Única
echo "🛒 FASE II: Comprando materiales de construcción..."
PURCHASE_RESP=$(curl -s -X POST http://localhost/v1/payments/purchase/start \
  -H "Content-Type: application/json" \
  -d '{"amount": "100000"}')

PURCHASE_REDIRECT=$(echo $PURCHASE_RESP | jq -r '.redirect_url')
echo "🔗 Autoriza la compra aquí: $PURCHASE_REDIRECT"
echo ""
read -p "Presiona Enter después de autorizar..."

echo ""
echo "🎉 ¡DEMO COMPLETADA!"
echo "✅ $100 USD enviados en remesas"
echo "✅ ~$1,000 MXN acumulados"
echo "✅ $1,000 MXN usados para materiales"
```

---

## 📝 Notas para el Hackathon

### Lo que funciona

✅ Flujo completo de autorización interactiva
✅ Grants con límites para pagos recurrentes
✅ Conversión de moneda USD → MXN
✅ Validación de hash según especificación
✅ Quotes dinámicos para tasas de cambio
✅ Pagos únicos y recurrentes

### Próximos pasos (fuera del alcance del prototipo)

- [ ] Frontend React para mejor UX
- [ ] Persistencia en base de datos
- [ ] Webhooks para automatización
- [ ] Manejo de errores más robusto
- [ ] Tests unitarios e integración
- [ ] Monitoreo y logging
- [ ] Scheduler para pagos recurrentes automáticos

---

## 🙋 Soporte

Para preguntas sobre el prototipo:
- Revisa la documentación de [Open Payments](https://openpayments.dev/)
- Consulta los logs: `docker compose logs -f backend`
- Verifica la configuración en `backend/app/app/core/config.py`

---

**Construido con ❤️ para el Interledger Hackathon 2025**
