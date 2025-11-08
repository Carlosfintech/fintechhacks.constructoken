"""
Configuración del Backend Constructoken
Variables de entorno y configuración de Rafiki
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# CONFIGURACIÓN DE RAFIKI
# ============================================================================

# URLs de los servicios de Rafiki
RAFIKI_ADMIN_URL = os.getenv("RAFIKI_ADMIN_URL", "http://localhost:3001/graphql")
RAFIKI_AUTH_URL = os.getenv("RAFIKI_AUTH_URL", "http://localhost:3006")
RAFIKI_RESOURCE_URL = os.getenv("RAFIKI_RESOURCE_URL", "http://localhost:3000")

# ============================================================================
# CONFIGURACIÓN DE WALLETS
# ============================================================================

def load_rafiki_config():
    """
    Carga la configuración de las WalletAddress desde el archivo JSON
    generado por setup_wallets.py
    """
    config_path = Path("rafiki_config.json")
    
    if not config_path.exists():
        # Configuración por defecto si no existe el archivo
        print("⚠️  rafiki_config.json no encontrado. Usando configuración por defecto.")
        print("   Ejecuta 'python setup_wallets.py' para crear las WalletAddress.")
        
        return {
            "assets": {
                "usd": {"id": "PENDING", "code": "USD", "scale": 2},
                "mxn": {"id": "PENDING", "code": "MXN", "scale": 2}
            },
            "wallets": {
                "pagador": {
                    "id": "PENDING",
                    "url": "http://localhost:3000/accounts/pagador",
                    "publicName": "Pagador Migrante"
                },
                "receptor": {
                    "id": "PENDING",
                    "url": "http://localhost:3000/accounts/receptor",
                    "publicName": "Proyecto FINSUS"
                },
                "capital": {
                    "id": "PENDING",
                    "url": "http://localhost:3000/accounts/capital",
                    "publicName": "Capital Marketplace"
                }
            }
        }
    
    with open(config_path, "r") as f:
        return json.load(f)

# Cargar configuración de Rafiki
RAFIKI_CONFIG = load_rafiki_config()

# ============================================================================
# CONFIGURACIÓN DE NEGOCIO
# ============================================================================

# Montos en centavos (scale=2)
STAGE_AMOUNT = 100000      # $1,000 MXN - Monto total de la etapa
PAYMENT_AMOUNT = 10000     # $100 MXN - Monto de cada pago individual
BNPL_AMOUNT = 20000        # $200 MXN - Monto que financia el marketplace
BNPL_PERCENTAGE = 0.20     # 20% del total

# Configuración de pagos
TOTAL_PAYMENTS = 10         # Total de pagos a realizar
BNPL_TRIGGER_PAYMENT = 8    # En qué pago se activa el BNPL
RECOVERY_PAYMENTS = 2       # Cuántos pagos para recuperar el BNPL

# ============================================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================================================

# Para el prototipo, usamos una BD en memoria (diccionario)
# En producción, configurar PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./constructoken.db")

# ============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ============================================================================

# JWT Secret (para un sistema de autenticación real)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================================

# FastAPI
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL", f"http://host.docker.internal:{PORT}/rafiki-webhook")

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# VALIDACIÓN
# ============================================================================

def validate_config():
    """Valida que la configuración sea correcta"""
    errors = []
    
    # Verificar que las WalletAddress estén configuradas
    if RAFIKI_CONFIG["wallets"]["pagador"]["id"] == "PENDING":
        errors.append("WalletAddress del Pagador no configurada")
    
    if RAFIKI_CONFIG["wallets"]["receptor"]["id"] == "PENDING":
        errors.append("WalletAddress del Receptor no configurada")
    
    if RAFIKI_CONFIG["wallets"]["capital"]["id"] == "PENDING":
        errors.append("WalletAddress de Capital no configurada")
    
    # Verificar que los montos sean consistentes
    if STAGE_AMOUNT != (PAYMENT_AMOUNT * TOTAL_PAYMENTS):
        errors.append(
            f"Inconsistencia en montos: "
            f"{PAYMENT_AMOUNT} × {TOTAL_PAYMENTS} ≠ {STAGE_AMOUNT}"
        )
    
    # Verificar que BNPL_AMOUNT sea correcto
    expected_bnpl = STAGE_AMOUNT - (PAYMENT_AMOUNT * BNPL_TRIGGER_PAYMENT)
    if BNPL_AMOUNT != expected_bnpl:
        errors.append(
            f"BNPL_AMOUNT incorrecto: "
            f"Esperado {expected_bnpl}, configurado {BNPL_AMOUNT}"
        )
    
    # Verificar que RECOVERY_PAYMENTS sea correcto
    if BNPL_AMOUNT != (PAYMENT_AMOUNT * RECOVERY_PAYMENTS):
        errors.append(
            f"RECOVERY_PAYMENTS incorrecto: "
            f"{PAYMENT_AMOUNT} × {RECOVERY_PAYMENTS} ≠ {BNPL_AMOUNT}"
        )
    
    if errors:
        print("\n⚠️  ERRORES DE CONFIGURACIÓN:")
        for error in errors:
            print(f"   ❌ {error}")
        print()
        
        if any("WalletAddress" in e for e in errors):
            print("💡 Solución: Ejecuta 'python setup_wallets.py' para configurar las WalletAddress")
    else:
        print("✅ Configuración validada correctamente")
    
    return len(errors) == 0

# ============================================================================
# HELPERS
# ============================================================================

def get_wallet_id(wallet_name: str) -> str:
    """Obtiene el ID de una wallet por su nombre"""
    return RAFIKI_CONFIG["wallets"][wallet_name]["id"]

def get_wallet_url(wallet_name: str) -> str:
    """Obtiene la URL de una wallet por su nombre"""
    return RAFIKI_CONFIG["wallets"][wallet_name]["url"]

def get_asset_id(asset_code: str) -> str:
    """Obtiene el ID de un asset por su código"""
    return RAFIKI_CONFIG["assets"][asset_code.lower()]["id"]

# ============================================================================
# INFORMACIÓN DEL SISTEMA
# ============================================================================

def print_config_info():
    """Imprime información de la configuración actual"""
    print("\n" + "="*60)
    print("CONFIGURACIÓN DE CONSTRUCTOKEN")
    print("="*60)
    
    print("\n🔧 URLs de Rafiki:")
    print(f"   Admin API: {RAFIKI_ADMIN_URL}")
    print(f"   Auth Server: {RAFIKI_AUTH_URL}")
    print(f"   Resource Server: {RAFIKI_RESOURCE_URL}")
    
    print("\n💰 Configuración de Negocio:")
    print(f"   Monto total etapa: ${STAGE_AMOUNT/100:.2f} MXN")
    print(f"   Monto por pago: ${PAYMENT_AMOUNT/100:.2f} MXN")
    print(f"   Total de pagos: {TOTAL_PAYMENTS}")
    print(f"   Trigger BNPL: Pago #{BNPL_TRIGGER_PAYMENT}")
    print(f"   Monto BNPL: ${BNPL_AMOUNT/100:.2f} MXN ({BNPL_PERCENTAGE*100}%)")
    print(f"   Pagos de recuperación: {RECOVERY_PAYMENTS}")
    
    print("\n🏦 WalletAddresses Configuradas:")
    for name, wallet in RAFIKI_CONFIG["wallets"].items():
        status = "✅" if wallet["id"] != "PENDING" else "⏳"
        print(f"   {status} {wallet['publicName']}")
        print(f"      ID: {wallet['id']}")
        print(f"      URL: {wallet['url']}")
    
    print("\n🌐 Assets Configurados:")
    for code, asset in RAFIKI_CONFIG["assets"].items():
        status = "✅" if asset["id"] != "PENDING" else "⏳"
        print(f"   {status} {asset['code']} (scale: {asset['scale']})")
    
    print("\n🔔 Webhook:")
    print(f"   URL: {WEBHOOK_URL}")
    
    print("\n⚙️  Servidor:")
    print(f"   Host: {HOST}")
    print(f"   Puerto: {PORT}")
    print(f"   Debug: {DEBUG}")
    
    print("\n" + "="*60 + "\n")

# ============================================================================
# EXPORTAR CONFIGURACIÓN COMO DICT
# ============================================================================

CONFIG_DICT = {
    "rafiki": {
        "admin_url": RAFIKI_ADMIN_URL,
        "auth_url": RAFIKI_AUTH_URL,
        "resource_url": RAFIKI_RESOURCE_URL
    },
    "business": {
        "stage_amount": STAGE_AMOUNT,
        "payment_amount": PAYMENT_AMOUNT,
        "total_payments": TOTAL_PAYMENTS,
        "bnpl_amount": BNPL_AMOUNT,
        "bnpl_trigger_payment": BNPL_TRIGGER_PAYMENT,
        "recovery_payments": RECOVERY_PAYMENTS
    },
    "wallets": RAFIKI_CONFIG["wallets"],
    "assets": RAFIKI_CONFIG["assets"],
    "server": {
        "host": HOST,
        "port": PORT,
        "debug": DEBUG
    }
}

# ============================================================================
# EJECUTAR VALIDACIÓN AL IMPORTAR
# ============================================================================

if __name__ == "__main__":
    print_config_info()
    validate_config()
