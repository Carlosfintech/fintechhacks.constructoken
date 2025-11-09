# 🧪 Configuración del Interledger Test Wallet

## Wallets Configuradas para Constructoken Hackathon

Esta guía documenta las 3 wallets ya configuradas en el **Interledger Test Wallet** para el prototipo del hackathon.

---

## 🎯 Wallets Disponibles

Ya tienes configuradas las siguientes 3 wallets en el Interledger Test Wallet:

### 1. 💵 US Wallet (USD) - "Pancho dolares"
- **Propósito**: Cuenta del migrante en Estados Unidos
- **Payment Pointer**: `$ilp.interledger-test.dev/pancho`
- **Wallet Address URL**: `https://ilp.interledger-test.dev/pancho`
- **Moneda**: USD (Dólares estadounidenses)
- **Balance Inicial**: $1,000 USD (o el monto fondeado)

### 2. 🇲🇽 Finsus Wallet (MXN) - "Pancho pesos"
- **Propósito**: Cuenta de ahorro del migrante en México (administrada por Finsus)
- **Payment Pointer**: `$ilp.interledger-test.dev/destinatario`
- **Wallet Address URL**: `https://ilp.interledger-test.dev/destinatario`
- **Moneda**: MXN (Pesos mexicanos)
- **Balance Inicial**: $0 MXN (se llenará con remesas)

### 3. 🏪 Merchant Wallet (MXN) - "merchant"
- **Propósito**: Cuenta del proveedor de materiales de construcción
- **Payment Pointer**: `$ilp.interledger-test.dev/merchant`
- **Wallet Address URL**: `https://ilp.interledger-test.dev/merchant`
- **Moneda**: MXN (Pesos mexicanos)
- **Balance Inicial**: $0 MXN (recibirá pagos)

---

## 📝 Información de Payment Pointers

### Formatos de Payment Pointer

Los Payment Pointers tienen dos formatos:

1. **Formato Corto** (Payment Pointer): Usado para enviar dinero fácilmente
   ```
   $ilp.interledger-test.dev/pancho
   ```

2. **Formato URL** (Wallet Address): Usado en las APIs de Open Payments
   ```
   https://ilp.interledger-test.dev/pancho
   ```

**Para este prototipo, usaremos el formato URL en las configuraciones.**

---

## 📝 Resumen de Direcciones

| Actor | Payment Pointer | Wallet Address (API) | Moneda |
|-------|----------------|----------------------|--------|
| **Migrante (USA)** | `$ilp.interledger-test.dev/pancho` | `https://ilp.interledger-test.dev/pancho` | USD |
| **Finsus (México)** | `$ilp.interledger-test.dev/destinatario` | `https://ilp.interledger-test.dev/destinatario` | MXN |
| **Merchant** | `$ilp.interledger-test.dev/merchant` | `https://ilp.interledger-test.dev/merchant` | MXN |

**Servidores Compartidos** (Testnet de Interledger):
- **Auth Server**: `https://auth.interledger-test.dev`
- **Resource Server**: `https://backend.interledger-test.dev`

---

## ⚙️ Configuración de Variables de Entorno

### Copiar archivo de plantilla

En tu proyecto:
```bash
cp env.template .env
```

### Editar `.env`

Abre el archivo `.env` y copia exactamente esta configuración:

```env
# ============================================================================
# INTERLEDGER TEST WALLET CONFIGURATION - CONSTRUCTOKEN HACKATHON
# ============================================================================

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/constructoken_hackathon

# FastAPI
APP_NAME=Constructoken Hackathon
DEBUG=True
API_VERSION=v1

# US Wallet (USD) - Pancho's account in the United States
US_WALLET_ADDRESS=https://ilp.interledger-test.dev/pancho
US_AUTH_SERVER=https://auth.interledger-test.dev
US_RESOURCE_SERVER=https://backend.interledger-test.dev

# Finsus Wallet (MXN) - Pancho's savings account in Mexico
FINSUS_WALLET_ADDRESS=https://ilp.interledger-test.dev/destinatario
FINSUS_AUTH_SERVER=https://auth.interledger-test.dev
FINSUS_RESOURCE_SERVER=https://backend.interledger-test.dev

# Merchant Wallet (MXN) - Materials supplier account
MERCHANT_WALLET_ADDRESS=https://ilp.interledger-test.dev/merchant
MERCHANT_AUTH_SERVER=https://auth.interledger-test.dev
MERCHANT_RESOURCE_SERVER=https://backend.interledger-test.dev

# Payment Configuration
RECURRING_PAYMENT_INTERVAL=weekly
RECURRING_PAYMENT_COUNT=10
TARGET_AMOUNT_MXN=1000.00
PAYMENT_AMOUNT_PER_INSTALLMENT_MXN=100.00

# Currency Configuration
BASE_CURRENCY_USD=USD
TARGET_CURRENCY_MXN=MXN

# Security
SECRET_KEY=constructoken-hackathon-2025-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**✅ Listo**: Las wallets ya están configuradas correctamente.

**⚠️ Solo necesitas actualizar**: La cadena de conexión de PostgreSQL en `DATABASE_URL` si es diferente.

---

## ✅ Verificar Configuración de las Wallets

### Probar Conexión a las Wallets

Verifica que las direcciones sean válidas y estén activas:

```bash
# Verificar US Wallet (USD - Pancho)
curl https://ilp.interledger-test.dev/pancho

# Verificar Finsus Wallet (MXN - Destinatario)
curl https://ilp.interledger-test.dev/destinatario

# Verificar Merchant Wallet (MXN)
curl https://ilp.interledger-test.dev/merchant
```

**Respuesta esperada**: Deberías recibir un JSON con información de cada wallet, similar a:

```json
{
  "id": "https://ilp.interledger-test.dev/pancho",
  "assetCode": "USD",
  "assetScale": 2,
  "authServer": "https://auth.interledger-test.dev"
}
```

### Verificar Fondos (Opcional)

Si tienes acceso al dashboard del Test Wallet, verifica:
- ✅ **US Wallet (pancho)**: Debería tener fondos en USD
- ✅ **Finsus Wallet (destinatario)**: Puede empezar en $0 MXN
- ✅ **Merchant Wallet (merchant)**: Puede empezar en $0 MXN

---

## 🎯 Resumen Final de Configuración

### Wallets Configuradas

| Wallet | Nombre | Moneda | Wallet Address (URL) |
|--------|--------|--------|----------------------|
| **US Wallet** | pancho | USD | `https://ilp.interledger-test.dev/pancho` |
| **Finsus Wallet** | destinatario | MXN | `https://ilp.interledger-test.dev/destinatario` |
| **Merchant Wallet** | merchant | MXN | `https://ilp.interledger-test.dev/merchant` |

### Servidores del Testnet

- **Auth Server**: `https://auth.interledger-test.dev`
- **Resource Server**: `https://backend.interledger-test.dev`

### Archivo `.env` Configurado

Tu archivo `.env` debe contener exactamente:

```env
US_WALLET_ADDRESS=https://ilp.interledger-test.dev/pancho
FINSUS_WALLET_ADDRESS=https://ilp.interledger-test.dev/destinatario
MERCHANT_WALLET_ADDRESS=https://ilp.interledger-test.dev/merchant

US_AUTH_SERVER=https://auth.interledger-test.dev
FINSUS_AUTH_SERVER=https://auth.interledger-test.dev
MERCHANT_AUTH_SERVER=https://auth.interledger-test.dev

US_RESOURCE_SERVER=https://backend.interledger-test.dev
FINSUS_RESOURCE_SERVER=https://backend.interledger-test.dev
MERCHANT_RESOURCE_SERVER=https://backend.interledger-test.dev
```

---

## 🔧 Troubleshooting

### Problema: "No puedo crear cuenta con MXN"

**Solución**: Algunas versiones del Test Wallet pueden tener limitaciones de monedas. Alternativas:

1. Usa USD para todas las cuentas (para propósitos de demo)
2. Contacta al soporte del Test Wallet
3. Usa cuentas existentes del testnet si están disponibles

### Problema: "Payment Pointer no responde"

**Solución**:
1. Verifica que copiaste la URL completa correctamente
2. Asegúrate de que la cuenta esté activa en el dashboard
3. Prueba accediendo a la URL en un navegador

### Problema: "Error de autorización en las APIs"

**Solución**:
1. Verifica que las URLs de auth y resource server sean exactamente:
   - `https://auth.interledger-test.dev`
   - `https://backend.interledger-test.dev`
2. No agregues `/` al final
3. No uses `http`, siempre `https`

---

## 📚 Recursos Adicionales

- **Documentación oficial del Test Wallet**: [Interledger Docs](https://interledger.org)
- **Open Payments API**: [https://openpayments.dev](https://openpayments.dev)
- **Snippets y ejemplos**: [https://openpayments.dev/snippets/](https://openpayments.dev/snippets/)

---

## 🎉 ¡Listo!

Ahora tienes configurado el Interledger Test Wallet y estás listo para ejecutar el prototipo.

**Siguiente paso**: Ejecutar la aplicación con:
```bash
./start.sh
```

Y seguir la **GUIA_RAPIDA.md** para la demo completa.

