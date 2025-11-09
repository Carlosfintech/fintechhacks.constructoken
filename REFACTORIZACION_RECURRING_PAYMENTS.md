# Refactorización de Pagos Recurrentes - Basado en Documentación Oficial

## 📋 Resumen

Se ha refactorizado completamente el código de pagos recurrentes (Caso 1) para seguir **exactamente** la documentación oficial de Open Payments.

**Documentación de referencia:** https://openpayments.dev/guides/recurring-subscription-incoming-amount/

## 🔄 Cambios Principales

### 1. **Schema RecurringPaymentGrant** (`backend/app/app/schemas/payments.py`)

**ANTES:**
```python
class RecurringPaymentGrant(BaseModel):
    sender_wallet: str
    receiver_wallet: str
    debit_amount_value: str
    total_amount_cap: str
    max_payments: int
```

**DESPUÉS:**
```python
class RecurringPaymentGrant(BaseModel):
    customer_wallet_address: str  # Wallet del cliente (Migrante)
    service_provider_wallet_address: str  # Wallet del proveedor (FINSUS)
    
    # Monto fijo que recibe el proveedor por pago
    incoming_amount_value: str
    incoming_amount_asset_code: str
    incoming_amount_asset_scale: int
    
    # Configuración de débito
    debit_amount_value: str
    debit_amount_asset_code: str
    debit_amount_asset_scale: int
    
    # Configuración de recurrencia
    interval: str  # Formato ISO 8601: R12/2025-10-14T00:03:00Z/P1M
    max_repetitions: int  # Extraído del interval
    payments_made: int
```

### 2. **Request Schema Simplificado** (`backend/app/app/schemas/payments.py`)

**ANTES:**
```python
class RecurringPaymentStartRequest(BaseModel):
    debit_amount: str
    total_cap: str
    interval: str
    max_payments: int
```

**DESPUÉS:**
```python
class RecurringPaymentStartRequest(BaseModel):
    incoming_amount: str  # Monto fijo que recibe el proveedor
    interval: str  # ISO 8601 repeating interval (e.g., 'R12/2025-10-14T00:03:00Z/P1M')
```

### 3. **Método start_recurring_grant_flow** (`backend/app/app/services/open_payments_service.py`)

**Cambios:**
- ✅ Sigue **Step 6** de la documentación oficial
- ✅ Extrae automáticamente `max_repetitions` del formato de `interval`
- ✅ Usa solo `debitAmount` e `interval` en los límites (sin `cap`)
- ✅ Actions correctos: `["create", "read"]` según documentación
- ✅ Logging detallado con prefijo `[RECURRING-STEP6]`

**Parámetros simplificados:**
```python
def start_recurring_grant_flow(
    self, 
    *, 
    incoming_amount: str,  # "1500" para $15.00
    interval: str,  # "R12/2025-10-14T00:03:00Z/P1M"
    redirect_uri_base: str
) -> tuple[str, ULID]
```

### 4. **Método complete_recurring_grant_flow** (`backend/app/app/services/open_payments_service.py`)

**Cambios:**
- ✅ Sigue **Step 9** de la documentación oficial
- ✅ Valida hash de respuesta (Step 8)
- ✅ Solicita grant continuation
- ✅ Almacena grant activo para ejecuciones futuras
- ✅ Logging detallado con prefijo `[RECURRING-STEP9]`

### 5. **Método execute_recurring_payment** (`backend/app/app/services/open_payments_service.py`) - **CAMBIO CRÍTICO**

**Refactorización completa siguiendo Steps 2-5 y 10:**

```python
def execute_recurring_payment(self, *, grant_id: ULID) -> Dict:
    """
    Ejecuta un pago recurrente individual.
    
    STEP 1: Obtener wallet addresses (cacheadas del setup inicial)
    
    STEP 2: Solicitar grant de incoming payment (service provider)
    - Type: "incoming-payment"
    - Actions: ["create"]
    
    STEP 3: Crear incoming payment en wallet del service provider
    - Usa el monto fijo: grant.incoming_amount_value
    - API: POST /incoming-payments
    
    STEP 4: Solicitar grant de quote (customer)
    - Type: "quote"
    - Actions: ["create"]
    
    STEP 5: Crear quote en wallet del customer
    - Receiver: incoming payment ID del Step 3
    - Method: "ilp"
    - API: POST /quotes
    
    STEP 10: Crear outgoing payment usando el recurring grant
    - QuoteId: del Step 5
    - AccessToken: grant.access_token (del grant recurrente!)
    - API: POST /outgoing-payments
    """
```

**Diferencias clave:**
- ❌ **ANTES:** Estimaba el monto en MXN con conversión hardcodeada
- ✅ **AHORA:** Usa el `incoming_amount_value` fijo del grant
- ❌ **ANTES:** Creaba grants sin seguir el orden de la documentación
- ✅ **AHORA:** Sigue exactamente Steps 2, 3, 4, 5 y 10
- ❌ **ANTES:** Usaba campos incorrectos (`sender_wallet`, `receiver_wallet`)
- ✅ **AHORA:** Usa `customer_wallet_address` y `service_provider_wallet_address`
- ✅ **AHORA:** Logging detallado por cada step con prefijos como `[RECURRING-STEP2]`

### 6. **Endpoints de API Actualizados** (`backend/app/app/api/api_v1/endpoints/payments.py`)

**POST /v1/payments/recurring/start**

```json
// ANTES
{
  "debit_amount": "1000",
  "total_cap": "10000",
  "interval": "R/2025-01-01T00:00:00Z/P1W",
  "max_payments": 10
}

// AHORA
{
  "incoming_amount": "1500",
  "interval": "R12/2025-10-14T00:03:00Z/P1M"
}
```

**Response incluye más información:**
```json
{
  "outgoing_payment_id": "...",
  "incoming_payment_id": "...",  // ✅ NUEVO
  "quote_id": "...",  // ✅ NUEVO
  "quote_debit_amount": "1500 USD",
  "quote_receive_amount": "30000 MXN",
  "payments_made": 1,
  "payments_remaining": 11
}
```

## 📊 Comparación del Flujo

### ANTES (Incorrecto)
1. ❌ Request interactive grant con `cap` y campos incorrectos
2. ❌ En execute: crear incoming payment con estimación de conversión
3. ❌ Crear quote y outgoing payment sin seguir estructura correcta

### AHORA (Según Documentación)
1. ✅ **Step 6:** Request interactive outgoing payment grant con `debitAmount` e `interval`
2. ✅ **Steps 7-8:** Usuario autoriza (interacción)
3. ✅ **Step 9:** Grant continuation (obtener access token)
4. ✅ **Para cada pago:**
   - **Step 2:** Request incoming payment grant (service provider)
   - **Step 3:** Create incoming payment con monto fijo
   - **Step 4:** Request quote grant (customer)
   - **Step 5:** Create quote
   - **Step 10:** Create outgoing payment con el recurring grant token

## 🔍 Mapeo de Terminología

| Documentación | Código Anterior | Código Refactorizado |
|---------------|-----------------|---------------------|
| Customer | sender / buyer | customer_wallet_address |
| Service Provider | receiver / seller | service_provider_wallet_address |
| Incoming Amount | N/A (estimado) | incoming_amount_value |
| Debit Amount | debit_amount | debit_amount_value |
| Interval | interval | interval |
| Repetitions | max_payments | max_repetitions |

## 🧪 Cómo Probar

### 1. Iniciar Grant Recurrente
```bash
curl -X POST http://localhost/v1/payments/recurring/start \
  -H "Content-Type: application/json" \
  -d '{
    "incoming_amount": "1500",
    "interval": "R12/2025-11-10T00:00:00Z/P1M"
  }'
```

**Respuesta:**
```json
{
  "redirect_url": "https://auth.wallet.example/...",
  "grant_id": "01HQXYZ..."
}
```

### 2. Usuario Autoriza (Steps 7-8)
- Abrir `redirect_url` en navegador
- Usuario autoriza el pago
- Redirect automático a: `http://localhost:3000/fulfil/recurring/{grant_id}?interact_ref=xxx&hash=yyy`

### 3. Callback (Step 9)
```bash
curl "http://localhost/v1/payments/recurring/callback?interact_ref=XXXX&hash=YYYY&grant_id=ZZZZ"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Recurring payment grant established successfully...",
  "grant_id": "01HQXYZ..."
}
```

### 4. Ejecutar Pago Recurrente (Steps 2-5, 10)
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
  "outgoing_payment_id": "https://wallet.example/outgoing-payments/abc",
  "incoming_payment_id": "https://wallet.example/incoming-payments/def",
  "quote_id": "https://wallet.example/quotes/ghi",
  "quote_debit_amount": "1500 USD",
  "quote_receive_amount": "30000 MXN",
  "payments_made": 1,
  "payments_remaining": 11
}
```

### 5. Repetir Step 4 para Pagos Subsecuentes
- Ejecutar `/recurring/trigger` hasta 12 veces (según interval R12)
- El grant se reutiliza automáticamente
- Los grants de incoming payment y quote se crean frescos cada vez

## 📚 Referencias de la Documentación

Cada método ahora incluye enlaces directos a la documentación:

1. **GET Wallet Address:** https://openpayments.dev/apis/wallet-address-server/operations/get-wallet-address/
2. **POST Grant Request:** https://openpayments.dev/apis/auth-server/operations/post-request/
3. **POST Create Incoming Payment:** https://openpayments.dev/apis/resource-server/operations/create-incoming-payment/
4. **POST Create Quote:** https://openpayments.dev/apis/resource-server/operations/create-quote/
5. **POST Grant Continuation:** https://openpayments.dev/apis/auth-server/operations/post-continue/
6. **POST Create Outgoing Payment:** https://openpayments.dev/apis/resource-server/operations/create-outgoing-payment/

## 🎯 Resultado

El código ahora implementa **exactamente** el patrón de "recurring subscription with fixed incoming amount" descrito en la documentación oficial de Open Payments, siguiendo el ejemplo de TypeScript transcrito correctamente a Python.

## 🔧 Logging Mejorado

Cada step ahora tiene logging detallado con prefijos:
- `[RECURRING-STEP6]` - Request interactive grant
- `[RECURRING-STEP9]` - Grant continuation
- `[RECURRING-STEP1]` - Get wallet addresses
- `[RECURRING-STEP2]` - Request incoming payment grant
- `[RECURRING-STEP3]` - Create incoming payment
- `[RECURRING-STEP4]` - Request quote grant
- `[RECURRING-STEP5]` - Create quote
- `[RECURRING-STEP10]` - Create outgoing payment
- `[RECURRING-EXECUTE]` - General execution logs

Esto facilita el debugging y permite rastrear exactamente qué step está fallando.

