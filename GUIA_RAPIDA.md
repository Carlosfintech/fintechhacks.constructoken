# 🚀 Guía Rápida - Constructoken Hackathon

Esta es una guía paso a paso para demostrar el prototipo en el hackathon.

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Configuración Inicial

```bash
# Clonar o navegar al proyecto
cd constructoken-hackathon

# Ejecutar script de inicio automático
./start.sh
```

El script `start.sh` hará:
- ✅ Crear entorno virtual
- ✅ Instalar dependencias
- ✅ Verificar configuración
- ✅ Inicializar base de datos
- ✅ Iniciar servidor FastAPI

### 2. Configurar Wallets en Interledger Test Wallet

**Antes de ejecutar**, necesitas crear 3 cuentas en [https://wallet.interledger-test.dev](https://wallet.interledger-test.dev):

#### Pasos rápidos:

1. **Crear cuenta principal**:
   - Ve a https://wallet.interledger-test.dev
   - Clic en "Create account"
   - Usa tu email real y una contraseña
   - Verifica tu email

2. **Crear 3 cuentas de wallet**:
   - **US Wallet (USD)**: "Migrant USD" con moneda USD, fondear con $1,000
   - **Finsus Wallet (MXN)**: "Finsus MXN" con moneda MXN, $0
   - **Merchant Wallet (MXN)**: "Merchant MXN" con moneda MXN, $0

3. **Copiar Payment Pointers**:
   Cada cuenta tendrá una dirección como:
   ```
   https://ilp.interledger-test.dev/[tu-usuario]/migrant-usd
   https://ilp.interledger-test.dev/[tu-usuario]/finsus-mxn
   https://ilp.interledger-test.dev/[tu-usuario]/merchant-mxn
   ```

4. **Actualizar `.env`**:
   ```env
   US_WALLET_ADDRESS=https://ilp.interledger-test.dev/[tu-usuario]/migrant-usd
   US_AUTH_SERVER=https://auth.interledger-test.dev
   US_RESOURCE_SERVER=https://backend.interledger-test.dev
   
   FINSUS_WALLET_ADDRESS=https://ilp.interledger-test.dev/[tu-usuario]/finsus-mxn
   FINSUS_AUTH_SERVER=https://auth.interledger-test.dev
   FINSUS_RESOURCE_SERVER=https://backend.interledger-test.dev
   
   MERCHANT_WALLET_ADDRESS=https://ilp.interledger-test.dev/[tu-usuario]/merchant-mxn
   MERCHANT_AUTH_SERVER=https://auth.interledger-test.dev
   MERCHANT_RESOURCE_SERVER=https://backend.interledger-test.dev
   ```

**Nota**: Todos usan el mismo auth y resource server porque están en el mismo testnet.

---

## 🎬 Demo del Flujo Completo

### Escenario

**Juan Pérez**, migrante en Estados Unidos, quiere construir una casa en Guadalajara, México. No tiene acceso a crédito, así que construirá por etapas.

**Etapa 1: Cimentación** - Costo: $1,000 MXN

Juan configurará pagos recurrentes de $100 MXN semanales (10 pagos) desde su cuenta en USA.

---

### Paso 1: Crear el Migrante

```bash
curl -X POST http://localhost:8000/migrants \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.perez@example.com",
    "full_name": "Juan Pérez",
    "phone": "+1-555-0123",
    "us_wallet_address": "https://ilp.interledger-test.dev/juan.perez/migrant-usd",
    "finsus_wallet_address": "https://ilp.interledger-test.dev/juan.perez/finsus-mxn"
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "email": "juan.perez@example.com",
  "full_name": "Juan Pérez",
  ...
}
```

✅ **Toma nota del ID**: `1`

---

### Paso 2: Crear el Proyecto de Construcción

```bash
curl -X POST "http://localhost:8000/projects?migrant_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Casa Familiar en Guadalajara",
    "description": "Construcción de vivienda de 80m² en 3 etapas",
    "location": "Guadalajara, Jalisco, México",
    "total_budget_mxn": 3000.0,
    "stages": [
      {
        "name": "Cimentación",
        "description": "Excavación, cimientos y platea",
        "order": 1,
        "target_amount_mxn": 1000.0
      },
      {
        "name": "Muros y Estructura",
        "description": "Construcción de muros principales y columnas",
        "order": 2,
        "target_amount_mxn": 1000.0
      },
      {
        "name": "Techo",
        "description": "Instalación de techo y terminaciones",
        "order": 3,
        "target_amount_mxn": 1000.0
      }
    ]
  }'
```

**Respuesta:**
```json
{
  "id": 1,
  "name": "Casa Familiar en Guadalajara",
  "stages": [
    {
      "id": 1,
      "name": "Cimentación",
      "target_amount_mxn": 1000.0,
      "current_amount_mxn": 0.0,
      "is_funded": false,
      ...
    },
    ...
  ]
}
```

✅ **Toma nota del Stage ID de "Cimentación"**: `1`

---

### Paso 3: Configurar Pagos Recurrentes (Fase I)

**🎯 Objetivo**: Fondear la etapa de Cimentación con 10 pagos semanales de $100 MXN

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

**Lo que sucede internamente:**

1. ✅ Se solicita autorización (GNAP) a la wallet USD
2. ✅ Se crea una cotización USD → MXN
3. ✅ Se configura el pago recurrente saliente
4. ✅ La wallet USD ejecutará 10 pagos automáticamente

**Respuesta:**
```json
{
  "id": 1,
  "stage_id": 1,
  "total_amount_mxn": 1000.0,
  "installment_amount_mxn": 100.0,
  "number_of_payments": 10,
  "interval": "weekly",
  "is_active": true,
  "payments_completed": 0,
  "grant_id": "grant-abc123",
  "quote_id": "quote-xyz789",
  "outgoing_payment_id": "payment-out-456"
}
```

✅ **Pagos recurrentes configurados!**

---

### Paso 4: Simular Ejecución de Pagos (Para Demo)

En producción, los pagos se ejecutarían automáticamente cada semana. Para la demo, simularemos los pagos:

```bash
# Simular los 10 pagos recurrentes
for i in {1..10}; do
  echo "💸 Simulando pago $i de 10..."
  curl -X POST http://localhost:8000/demo/simulate-payment-completion \
    -H "Content-Type: application/json" \
    -d "{
      \"payment_id\": \"payment-out-456-$i\",
      \"payment_type\": \"recurring\"
    }"
  echo ""
  sleep 0.5
done
```

**Cada pago:**
- ✅ Agrega $100 MXN a la etapa
- ✅ Crea un registro de transacción
- ✅ Actualiza el progreso

---

### Paso 5: Verificar Progreso de Ahorro

```bash
curl http://localhost:8000/stages/1/funding-status
```

**Respuesta:**
```json
{
  "stage_id": 1,
  "stage_name": "Cimentación",
  "target_amount_mxn": 1000.0,
  "current_amount_mxn": 1000.0,
  "is_funded": true,
  "is_purchased": false,
  "funding_progress_percentage": 100.0,
  "payments_completed": 10,
  "total_payments": 10
}
```

🎉 **¡Meta alcanzada! La etapa está completamente fondeada.**

---

### Paso 6: Comprar Materiales (Fase II)

Ahora que Juan tiene $1,000 MXN en su wallet Finsus, puede comprar los materiales.

```bash
curl -X POST http://localhost:8000/material-purchases \
  -H "Content-Type: application/json" \
  -d '{
    "stage_id": 1,
    "merchant_name": "Materiales de Construcción López",
    "merchant_wallet_address": "https://ilp.interledger-test.dev/juan.perez/merchant-mxn",
    "items_description": "Cemento (50 bultos), Arena (2m³), Grava (2m³), Varilla corrugada #3 (100 piezas)",
    "delivery_address": "Calle Revolución 456, Col. Centro, Guadalajara, Jalisco, C.P. 44100",
    "delivery_notes": "Entregar entre 8am - 12pm. Llamar 30 minutos antes."
  }'
```

**Lo que sucede internamente:**

1. ✅ Verifica que la etapa esté fondeada
2. ✅ El merchant crea un "incoming payment" (factura)
3. ✅ Se solicita autorización de la wallet Finsus
4. ✅ Se crea cotización para el pago
5. ✅ Se ejecuta el pago Finsus → Merchant
6. ✅ Se completa el incoming payment

**Respuesta:**
```json
{
  "id": 1,
  "stage_id": 1,
  "merchant_name": "Materiales de Construcción López",
  "total_amount_mxn": 1000.0,
  "buyer_wallet_address": "https://...finsus.../juan-mxn",
  "merchant_wallet_address": "https://...merchant-lopez",
  "status": "processing",
  "delivery_address": "Calle Revolución 456...",
  "incoming_payment_id": "incoming-abc123",
  "outgoing_payment_id": "outgoing-xyz789",
  ...
}
```

---

### Paso 7: Verificar Estado de Compra

```bash
curl http://localhost:8000/material-purchases/1/status
```

**Respuesta:**
```json
{
  "purchase_id": 1,
  "stage_id": 1,
  "merchant_name": "Materiales de Construcción López",
  "amount_mxn": 1000.0,
  "status": "completed",
  "delivery_address": "Calle Revolución 456...",
  "created_at": "2025-11-09T...",
  "completed_at": "2025-11-09T...",
  "outgoing_payment_status": {...},
  "incoming_payment_status": {...}
}
```

🎉 **¡Compra completada! Los materiales van en camino.**

---

### Paso 8: Ver Historial de Transacciones

```bash
curl http://localhost:8000/transactions?stage_id=1
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "stage_id": 1,
    "payment_type": "recurring_remittance",
    "amount_mxn": 100.0,
    "status": "completed",
    ...
  },
  {
    "id": 2,
    "payment_type": "recurring_remittance",
    "amount_mxn": 100.0,
    ...
  },
  ...
  {
    "id": 11,
    "payment_type": "one_time_purchase",
    "amount_mxn": 1000.0,
    "status": "completed",
    ...
  }
]
```

---

## 📊 Ver la Documentación Interactiva

Abre tu navegador en:

**Swagger UI**: http://localhost:8000/docs

Aquí podrás:
- ✅ Ver todos los endpoints disponibles
- ✅ Probar requests directamente desde el navegador
- ✅ Ver schemas de request/response
- ✅ Generar ejemplos automáticamente

**ReDoc**: http://localhost:8000/redoc (documentación más visual)

---

## 🎯 Puntos Clave para la Demo

### Fase I: Pagos Recurrentes USD → MXN

**Open Payments Use Case**: "Send recurring remittances with a fixed debit amount"

✅ **Demuestra:**
- Autorización con GNAP
- Conversión automática USD → MXN
- Pagos recurrentes programados
- Actualización automática del progreso de ahorro
- Notificaciones vía webhooks

### Fase II: Compra Única MXN → Merchant

**Open Payments Use Case**: "Accept a one-time payment for an online purchase"

✅ **Demuestra:**
- Creación de factura (incoming payment)
- Autorización de pago único
- Pago entre wallets en misma moneda (MXN)
- Completado con verificación criptográfica
- Estado final de la compra

---

## 🔄 Flujo Completo en Producción

```
Migrante en USA
    │
    │ [Configura pagos recurrentes]
    ▼
US Wallet (USD)
    │
    │ [10 pagos semanales, automáticos]
    │ [Conversión USD → MXN vía ILP]
    ▼
Finsus Wallet (MXN)
    │
    │ [Ahorro incrementa cada semana]
    │ [Webhook notifica a Constructoken]
    ▼
Meta Alcanzada ($1,000 MXN)
    │
    │ [Usuario hace clic en "Comprar Materiales"]
    ▼
Merchant crea factura
    │
    │ [Pago único MXN → MXN]
    ▼
Merchant recibe fondos
    │
    ▼
Materiales se entregan 📦
```

---

## 🐛 Troubleshooting

### Error: "Database connection failed"

```bash
# Verificar que PostgreSQL esté corriendo
brew services start postgresql
# o
sudo service postgresql start

# Crear la base de datos
createdb constructoken_hackathon
```

### Error: "Stage not funded"

```bash
# Verificar el estado de la etapa
curl http://localhost:8000/stages/1/funding-status

# Si current_amount_mxn < target_amount_mxn, simula más pagos
curl -X POST http://localhost:8000/demo/simulate-payment-completion ...
```

### Error: "Wallet address not configured"

Verifica tu archivo `.env`:
```bash
cat .env | grep WALLET_ADDRESS
```

Asegúrate de que las direcciones sean válidas del Interledger Test Wallet.

### Error: "Grant request failed"

Asegúrate de que:
1. Las wallets tengan fondos suficientes
2. Las URLs de auth y resource server sean correctas:
   - Auth: `https://auth.interledger-test.dev`
   - Resource: `https://backend.interledger-test.dev`

---

## 📚 Recursos Adicionales

- **README completo**: `README.md`
- **Arquitectura técnica**: `ARQUITECTURA.md`
- **Documentación de Open Payments**: https://openpayments.dev
- **Interledger Test Wallet**: https://wallet.interledger-test.dev
- **Hackathon Interledger**: https://interledger.org/es/summit/hackaton

---

## 🎤 Talking Points para la Presentación

1. **Problema Real**: 
   - Migrantes envían $60 mil millones USD a México anualmente
   - Dificultad para ahorrar y construir vivienda
   - Fugas de dinero y falta de planificación

2. **Solución con Open Payments**:
   - Pagos transfronterizos transparentes y económicos
   - Automatización de ahorro mediante pagos recurrentes
   - Protocolo estándar, interoperable entre ASEs

3. **Impacto Social**:
   - Acceso a vivienda para familias sin crédito
   - Empoderamiento financiero de migrantes
   - Economía formal y transparente

4. **Innovación Técnica**:
   - Primera implementación de Open Payments en construcción
   - Dos casos de uso integrados (recurring + one-time)
   - Arquitectura escalable y extensible

---

**¡Listo para impresionar en el hackathon! 🚀🏆**

