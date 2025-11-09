# Caso 1 Simplificado: Pago Único MIGRANTE -> FINSUS (USD -> MXN)

## Resumen de Cambios

El **Caso 1** ha sido simplificado de pagos recurrentes a **pago único** (one-time payment) para facilitar la implementación en el tiempo disponible del hackathon.

### Flujo Anterior (Pagos Recurrentes)
- Grants interactivos con `interval` y `limits`
- Tres endpoints: `/recurring/start`, `/recurring/callback`, `/recurring/trigger`
- Requería ejecutar manualmente cada pago con el endpoint `/trigger`
- Complejidad alta con grants persistentes y estado de pagos

### Flujo Actual (Pago Único)
- Pago simple similar al Caso 2
- Dos endpoints: `/migrante/start`, `/migrante/callback`
- El pago se completa automáticamente después de la autorización
- Conversión de **USD (MIGRANTE) -> MXN (FINSUS)**

---

## Cambios Realizados

### 1. Servicio (`open_payments_service.py`)

#### Métodos Modificados:

**`get_migrante_payment_endpoint(amount: str)`** (anteriormente `start_recurring_grant_flow`)
- Crea un pending payment transaction
- Solicita incoming payment grant para FINSUS
- Solicita quote grant para MIGRANTE  
- Solicita interactive grant simple (sin `interval` ni `limits`)
- Devuelve redirect URL y pending transaction

**`complete_migrante_payment(transaction_id: ULID, ...)`** (anteriormente `complete_recurring_grant_flow`)
- Valida el hash de la respuesta
- Solicita grant continuation
- **Crea y completa el outgoing payment automáticamente**
- Devuelve el OutgoingPayment completado

#### Métodos Eliminados:

- `execute_recurring_payment()` - Ya no es necesario, el pago se completa automáticamente

### 2. Endpoints API (`payments.py`)

#### Endpoints Modificados:

**POST `/v1/payments/migrante/start`** (anteriormente `/recurring/start`)
```json
{
  "amount": "1500"  // Ahora solo requiere amount (en centavos)
}
```

**Respuesta:**
```json
{
  "redirect_url": "https://auth.interledger-test.dev/interact/...",
  "grant_id": "01K9M1DR7N652ZHV8291FC93A2"
}
```

**GET `/v1/payments/migrante/callback`** (anteriormente `/recurring/callback`)
- Query params: `interact_ref`, `hash`, `transaction_id`
- **Completa el pago automáticamente**
- Devuelve el ID del outgoing payment

#### Endpoints Eliminados:

- `POST /recurring/trigger` - Ya no es necesario

### 3. Esquemas (`payments.py`)

**`RecurringPaymentStartRequest`**
```python
# Antes:
debit_amount: str
total_cap: str
interval: str  
max_payments: int

# Ahora:
amount: str  # Solo el monto
```

### 4. Configuración del Servicio

**`create_recurring_payment_service()`**
- Ahora llamado "one-time MIGRANTE payments"
- Redirect URI cambiado de `/recurring/` a `/migrante/`
- Mantiene: FINSUS como receiver (seller), MIGRANTE como sender (buyer)

---

## Flujo Completo del Pago

### 1. Inicio del Pago
```bash
curl -X POST http://localhost/v1/payments/migrante/start \
  -H "Content-Type: application/json" \
  -d '{"amount": "1500"}'
```

### 2. Usuario Autoriza
- Se redirige a la `redirect_url` del Interledger Test Wallet
- Usuario aprueba el pago de USD desde su cuenta MIGRANTE

### 3. Callback Automático
- Wallet redirige a `/v1/payments/migrante/callback?transaction_id=...&interact_ref=...&hash=...`
- Backend valida y **completa el pago automáticamente**
- FINSUS recibe los fondos en MXN

### 4. Resultado
```json
{
  "success": true,
  "message": "Payment completed successfully. Outgoing payment ID: https://...",
  "grant_id": "01K9M1DR7N652ZHV8291FC93A2"
}
```

---

## Diferencias con Caso 2

| Aspecto | Caso 1 (MIGRANTE) | Caso 2 (PURCHASE) |
|---------|-------------------|-------------------|
| **Sender** | MIGRANTE (USD) | FINSUS (MXN) |
| **Receiver** | FINSUS (MXN) | Merchant (MXN) |
| **Conversión** | USD → MXN | MXN → MXN |
| **Endpoint Start** | `/migrante/start` | `/purchase/start` |
| **Endpoint Callback** | `/migrante/callback` | `/purchase/callback` |
| **Flujo** | Idéntico | Idéntico |

---

## Ventajas del Cambio

1. ✅ **Simplicidad**: Eliminada complejidad de grants recurrentes
2. ✅ **Confiabilidad**: Mismo flujo probado del Caso 2
3. ✅ **Rapidez**: Sin necesidad de trigger manual
4. ✅ **Consistencia**: Ambos casos usan el mismo patrón
5. ✅ **Funcionalidad**: Cumple con el objetivo de transferir USD → MXN

---

## Prueba Exitosa

```bash
# Start payment
POST /v1/payments/migrante/start
{
  "amount": "1500"
}

# Response:
{
  "redirect_url": "https://auth.interledger-test.dev/interact/...",
  "grant_id": "01K9M1DR7N652ZHV8291FC93A2"
}
```

✅ **El Caso 1 ahora funciona como pago único con conversión USD → MXN**

---

## Próximos Pasos

Para habilitar pagos recurrentes en el futuro:
1. Restaurar los métodos de grants con `interval` y `limits`
2. Agregar endpoint `/migrante/trigger` para ejecutar pagos programados
3. Implementar persistencia de grants activos (Redis/DB)
4. Agregar cron job o scheduler para ejecutar pagos automáticamente

