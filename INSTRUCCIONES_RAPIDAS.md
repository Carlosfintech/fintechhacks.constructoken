# ⚡ Instrucciones Rápidas - Inicio en 5 Minutos

## 🎯 Wallets Ya Configuradas

Las 3 wallets del Interledger Test Wallet están listas:

| Wallet | Payment Pointer | Moneda | Propósito |
|--------|-----------------|--------|-----------|
| **Pancho** | `$ilp.interledger-test.dev/pancho` | USD | Migrante en USA |
| **Destinatario** | `$ilp.interledger-test.dev/destinatario` | MXN | Ahorro en México |
| **Merchant** | `$ilp.interledger-test.dev/merchant` | MXN | Proveedor materiales |

---

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Configurar Variables de Entorno

```bash
# Copiar archivo pre-configurado
cp env.hackathon.template .env

# Editar SOLO la línea de DATABASE_URL
nano .env  # o tu editor favorito
```

**Actualiza esta línea:**
```env
DATABASE_URL=postgresql://TU_USUARIO:TU_PASSWORD@localhost:5432/constructoken_hackathon
```

### 2️⃣ Crear Base de Datos

```bash
# Crear la base de datos
createdb constructoken_hackathon

# O usando psql
psql -U postgres -c "CREATE DATABASE constructoken_hackathon;"
```

### 3️⃣ Iniciar Aplicación

```bash
# El script hace todo automáticamente
./start.sh
```

¡Listo! 🎉 La API estará en http://localhost:8000

---

## 📡 Verificar que Funciona

### Prueba 1: Health Check

```bash
curl http://localhost:8000/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "open_payments": "configured"
}
```

### Prueba 2: Verificar Wallets

```bash
# Verificar US Wallet
curl https://ilp.interledger-test.dev/pancho

# Verificar Finsus Wallet
curl https://ilp.interledger-test.dev/destinatario

# Verificar Merchant Wallet
curl https://ilp.interledger-test.dev/merchant
```

Cada uno debería devolver información de la wallet en JSON.

---

## 🎬 Demo Rápida (5 minutos)

Sigue estos pasos para ver el flujo completo:

### 1. Crear Migrante

```bash
curl -X POST http://localhost:8000/migrants \
  -H "Content-Type: application/json" \
  -d '{
    "email": "pancho@example.com",
    "full_name": "Pancho",
    "phone": "+1-555-0100",
    "us_wallet_address": "https://ilp.interledger-test.dev/pancho",
    "finsus_wallet_address": "https://ilp.interledger-test.dev/destinatario"
  }'
```

✅ Toma nota del `id` que devuelve (probablemente `1`)

### 2. Crear Proyecto con Etapas

```bash
curl -X POST "http://localhost:8000/projects?migrant_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Casa de Pancho",
    "description": "Construcción en México",
    "location": "Guadalajara, Jalisco",
    "total_budget_mxn": 1000.0,
    "stages": [
      {
        "name": "Cimentación",
        "description": "Base de la casa",
        "order": 1,
        "target_amount_mxn": 1000.0
      }
    ]
  }'
```

✅ Toma nota del `stage_id` (probablemente `1`)

### 3. Configurar Pagos Recurrentes (USD → MXN)

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

**Esto configura**: 10 pagos semanales de $100 MXN desde la wallet USD (pancho) hacia la wallet MXN (destinatario).

### 4. Simular Pagos Completados

```bash
# Simular los 10 pagos
for i in {1..10}; do
  curl -X POST http://localhost:8000/demo/simulate-payment-completion \
    -H "Content-Type: application/json" \
    -d "{\"payment_id\": \"payment-$i\", \"payment_type\": \"recurring\"}"
  echo " - Pago $i completado"
done
```

### 5. Verificar Meta Alcanzada

```bash
curl http://localhost:8000/stages/1/funding-status
```

Deberías ver:
```json
{
  "stage_id": 1,
  "stage_name": "Cimentación",
  "target_amount_mxn": 1000.0,
  "current_amount_mxn": 1000.0,
  "is_funded": true,
  "funding_progress_percentage": 100.0,
  "payments_completed": 10,
  "total_payments": 10
}
```

### 6. Comprar Materiales (MXN → Merchant)

```bash
curl -X POST http://localhost:8000/material-purchases \
  -H "Content-Type: application/json" \
  -d '{
    "stage_id": 1,
    "merchant_name": "Materiales López",
    "merchant_wallet_address": "https://ilp.interledger-test.dev/merchant",
    "items_description": "Cemento, arena, grava",
    "delivery_address": "Guadalajara, Jalisco",
    "delivery_notes": "Entregar en la mañana"
  }'
```

**Esto ejecuta**: Pago único de $1,000 MXN desde la wallet Finsus (destinatario) hacia la wallet del comerciante (merchant).

### 7. Verificar Compra

```bash
curl http://localhost:8000/material-purchases/1/status
```

---

## 📊 Ver en Swagger UI

Abre tu navegador en:

**http://localhost:8000/docs**

Aquí puedes:
- Ver todos los endpoints
- Probar las APIs interactivamente
- Ver ejemplos de requests/responses

---

## 🔧 Troubleshooting Rápido

### Error: "Database connection failed"

```bash
# Verificar que PostgreSQL esté corriendo
brew services list  # macOS
sudo service postgresql status  # Linux

# Verificar que la base de datos exista
psql -l | grep constructoken
```

### Error: "Wallet address not found"

Las wallets están pre-configuradas correctamente en `.env.hackathon`. Si ves este error:

1. Verifica que copiaste `.env.hackathon` a `.env`
2. Verifica que no modificaste las URLs de las wallets

### Error: "Grant request failed"

Esto puede pasar si las wallets no tienen fondos. Para la demo, usa los endpoints de simulación:
```bash
curl -X POST http://localhost:8000/demo/simulate-payment-completion ...
```

---

## 📚 Documentación Completa

- **SETUP_TESTNET.md** - Configuración detallada de wallets
- **GUIA_RAPIDA.md** - Tutorial completo de la demo
- **README.md** - Documentación del proyecto
- **ARQUITECTURA.md** - Diagramas técnicos
- **PRESENTACION_HACKATHON.md** - Script para presentar

---

## 🎯 Siguiente Paso

Una vez que funciona localmente, consulta **GUIA_RAPIDA.md** para la demo completa con explicaciones detalladas de cada paso.

**¡Éxito en el hackathon! 🚀🏆**

