#!/usr/bin/env python3
"""
Setup Completo de Constructoken + Rafiki
Automatiza la configuración inicial del prototipo
"""

import requests
import json
import time
import sys
import os
import hmac
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import canonicaljson

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

RAFIKI_ADMIN_URL = os.getenv("RAFIKI_ADMIN_URL", "http://localhost:3001/graphql")
RAFIKI_API_SECRET = os.getenv("RAFIKI_API_SECRET", "")
RAFIKI_TENANT_ID = os.getenv("RAFIKI_TENANT_ID", "")

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

# ============================================================================
# VERIFICACIONES
# ============================================================================

def check_rafiki():
    """Verifica que Rafiki esté corriendo"""
    print_info("Verificando conexión con Rafiki...")
    try:
        body = {"query": "{ __typename }"}
        headers = {"Content-Type": "application/json"}

        # Add authentication if available
        if RAFIKI_API_SECRET and RAFIKI_TENANT_ID:
            signature = generate_api_signature(body, RAFIKI_API_SECRET)
            headers["signature"] = signature
            headers["tenant-id"] = RAFIKI_TENANT_ID

        response = requests.post(
            RAFIKI_ADMIN_URL,
            json=body,
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print_success("Rafiki está corriendo y responde")
            return True
        else:
            print_error(f"Rafiki responde con error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"No se puede conectar a Rafiki: {str(e)}")
        print_warning("Asegúrate de que Rafiki esté corriendo:")
        print_info("  cd rafiki && pnpm localenv:compose up -d")
        return False

# ============================================================================
# FUNCIONES DE GRAPHQL
# ============================================================================

def generate_api_signature(body_dict, secret):
    """
    Genera la firma HMAC para autenticación con Rafiki Admin API

    Format: t=timestamp, v=version, h=digest
    Payload: timestamp.canonicalized_json
    """
    timestamp = str(int(time.time() * 1000))  # milliseconds
    version = "1"

    # Canonicalize JSON using RFC 8785
    canonical_json = canonicaljson.encode_canonical_json(body_dict).decode('utf-8')

    # Create payload
    payload = f"{timestamp}.{canonical_json}"

    # Generate HMAC-SHA256
    signature_hmac = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    )
    digest = signature_hmac.hexdigest()

    # Format signature
    signature = f"t={timestamp}, v={version}, h={digest}"
    return signature


def execute_graphql(query, variables=None):
    """Ejecuta una query GraphQL contra Rafiki"""
    try:
        body = {"query": query, "variables": variables or {}}

        headers = {
            "Content-Type": "application/json"
        }

        # Add authentication headers if available
        if RAFIKI_API_SECRET and RAFIKI_TENANT_ID:
            signature = generate_api_signature(body, RAFIKI_API_SECRET)
            headers["signature"] = signature
            headers["tenant-id"] = RAFIKI_TENANT_ID

        response = requests.post(
            RAFIKI_ADMIN_URL,
            json=body,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        if "errors" in result:
            raise Exception(f"GraphQL Error: {result['errors']}")

        return result.get("data", {})
    except Exception as e:
        raise Exception(f"Error ejecutando GraphQL: {str(e)}")

def get_or_create_asset(code, scale):
    """Obtiene un asset existente o lo crea si no existe"""
    # Primero intentar obtener assets existentes
    query = """
    query ListAssets {
      assets {
        edges {
          node {
            id
            code
            scale
          }
        }
      }
    }
    """
    
    try:
        result = execute_graphql(query)
        assets = result.get("assets", {}).get("edges", [])
        
        for edge in assets:
            asset = edge["node"]
            if asset["code"] == code and asset["scale"] == scale:
                print_info(f"Asset {code} ya existe: {asset['id']}")
                return asset
    except Exception as e:
        print_warning(f"Error buscando assets: {str(e)}")
    
    # Si no existe, crear
    print_info(f"Creando asset {code}...")
    mutation = """
    mutation CreateAsset($input: CreateAssetInput!) {
      createAsset(input: $input) {
        code
        success
        message
        asset {
          id
          code
          scale
        }
      }
    }
    """
    
    variables = {
        "input": {
            "code": code,
            "scale": scale
        }
    }
    
    result = execute_graphql(mutation, variables)
    asset_result = result.get("createAsset", {})
    
    if asset_result.get("success"):
        asset = asset_result.get("asset")
        print_success(f"Asset {code} creado: {asset['id']}")
        return asset
    else:
        raise Exception(f"Error creando asset: {asset_result.get('message')}")

def create_wallet_address(name, asset_id, url):
    """Crea una WalletAddress"""
    print_info(f"Creando WalletAddress: {name}...")
    
    mutation = """
    mutation CreateWalletAddress($input: CreateWalletAddressInput!) {
      createWalletAddress(input: $input) {
        code
        success
        message
        walletAddress {
          id
          url
          publicName
          asset {
            id
            code
            scale
          }
        }
      }
    }
    """
    
    variables = {
        "input": {
            "assetId": asset_id,
            "publicName": name,
            "url": url
        }
    }
    
    result = execute_graphql(mutation, variables)
    wallet_result = result.get("createWalletAddress", {})
    
    if wallet_result.get("success"):
        wallet = wallet_result.get("walletAddress")
        print_success(f"WalletAddress creada: {name}")
        print_info(f"  ID: {wallet['id']}")
        print_info(f"  URL: {wallet['url']}")
        return wallet
    else:
        raise Exception(f"Error creando wallet: {wallet_result.get('message')}")

def create_webhook_endpoint(url):
    """Crea un webhook endpoint"""
    print_info(f"Configurando webhook: {url}...")
    
    mutation = """
    mutation CreateWebhookEndpoint($input: CreateWebhookEndpointInput!) {
      createWebhookEndpoint(input: $input) {
        code
        success
        message
        webhookEndpoint {
          id
          url
        }
      }
    }
    """
    
    variables = {
        "input": {
            "url": url
        }
    }
    
    try:
        result = execute_graphql(mutation, variables)
        webhook_result = result.get("createWebhookEndpoint", {})
        
        if webhook_result.get("success"):
            webhook = webhook_result.get("webhookEndpoint")
            print_success(f"Webhook configurado: {webhook['id']}")
            return webhook
        else:
            print_warning(f"Webhook ya existe o error: {webhook_result.get('message')}")
            return None
    except Exception as e:
        print_warning(f"Error configurando webhook: {str(e)}")
        return None

# ============================================================================
# PROCESO PRINCIPAL
# ============================================================================

def main():
    print_header("SETUP DE CONSTRUCTOKEN + RAFIKI")
    
    # 1. Verificar Rafiki
    print_header("1. VERIFICANDO SERVICIOS")
    if not check_rafiki():
        print_error("\n⚠️  Setup abortado. Inicia Rafiki primero:")
        print_info("  cd rafiki")
        print_info("  pnpm localenv:compose up -d")
        sys.exit(1)
    
    print_success("Todos los servicios están operativos\n")
    time.sleep(1)
    
    # 2. Crear Assets
    print_header("2. CONFIGURANDO ASSETS (MONEDAS)")
    
    try:
        usd_asset = get_or_create_asset("USD", 2)
        mxn_asset = get_or_create_asset("MXN", 2)
    except Exception as e:
        print_error(f"Error configurando assets: {str(e)}")
        sys.exit(1)
    
    print_success("Assets configurados correctamente\n")
    time.sleep(1)
    
    # 3. Crear WalletAddresses
    print_header("3. CREANDO WALLET ADDRESSES")
    
    wallets = {}
    
    try:
        # Pagador (USD)
        wallets["pagador"] = create_wallet_address(
            "Pagador Migrante",
            usd_asset["id"],
            "http://localhost:3000/accounts/pagador"
        )
        
        # Receptor (MXN)
        wallets["receptor"] = create_wallet_address(
            "Proyecto FINSUS",
            mxn_asset["id"],
            "http://localhost:3000/accounts/receptor"
        )
        
        # Capital (MXN)
        wallets["capital"] = create_wallet_address(
            "Capital Marketplace",
            mxn_asset["id"],
            "http://localhost:3000/accounts/capital"
        )
    except Exception as e:
        print_error(f"Error creando wallets: {str(e)}")
        sys.exit(1)
    
    print_success("Todas las WalletAddresses creadas\n")
    time.sleep(1)
    
    # 4. Configurar Webhook
    print_header("4. CONFIGURANDO WEBHOOK")
    
    webhook_url = "http://host.docker.internal:8000/rafiki-webhook"
    webhook = create_webhook_endpoint(webhook_url)
    
    print_success("Webhook configurado\n")
    time.sleep(1)
    
    # 5. Guardar configuración
    print_header("5. GUARDANDO CONFIGURACIÓN")
    
    config = {
        "assets": {
            "usd": {
                "id": usd_asset["id"],
                "code": usd_asset["code"],
                "scale": usd_asset["scale"]
            },
            "mxn": {
                "id": mxn_asset["id"],
                "code": mxn_asset["code"],
                "scale": mxn_asset["scale"]
            }
        },
        "wallets": {
            "pagador": {
                "id": wallets["pagador"]["id"],
                "url": wallets["pagador"]["url"],
                "publicName": wallets["pagador"]["publicName"]
            },
            "receptor": {
                "id": wallets["receptor"]["id"],
                "url": wallets["receptor"]["url"],
                "publicName": wallets["receptor"]["publicName"]
            },
            "capital": {
                "id": wallets["capital"]["id"],
                "url": wallets["capital"]["url"],
                "publicName": wallets["capital"]["publicName"]
            }
        },
        "webhook": {
            "id": webhook["id"] if webhook else "N/A",
            "url": webhook_url
        }
    }
    
    config_file = Path("rafiki_config.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print_success(f"Configuración guardada en: {config_file}")
    
    # 6. Resumen
    print_header("✅ SETUP COMPLETADO")
    
    print("\n" + "="*60)
    print(f"{Colors.BOLD}RESUMEN DE LA CONFIGURACIÓN{Colors.ENDC}")
    print("="*60)
    
    print(f"\n{Colors.OKCYAN}📋 Assets Creados:{Colors.ENDC}")
    print(f"   • USD (scale=2): {usd_asset['id']}")
    print(f"   • MXN (scale=2): {mxn_asset['id']}")
    
    print(f"\n{Colors.OKCYAN}🏦 WalletAddresses Creadas:{Colors.ENDC}")
    for name, wallet in wallets.items():
        print(f"   • {wallet['publicName']}")
        print(f"     ID: {wallet['id']}")
        print(f"     URL: {wallet['url']}")
    
    print(f"\n{Colors.OKCYAN}🔔 Webhook:{Colors.ENDC}")
    print(f"   • URL: {webhook_url}")
    if webhook:
        print(f"   • ID: {webhook['id']}")
    
    print(f"\n{Colors.OKCYAN}📁 Archivo de Configuración:{Colors.ENDC}")
    print(f"   • rafiki_config.json")
    
    print("\n" + "="*60)
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ¡Todo listo!{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Siguiente paso:{Colors.ENDC}")
    print(f"  {Colors.OKCYAN}python main.py{Colors.ENDC}     # Inicia el backend")
    print(f"  {Colors.OKCYAN}python demo.py{Colors.ENDC}     # Ejecuta la demo")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelado por el usuario{Colors.ENDC}\n")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError inesperado: {str(e)}")
        sys.exit(1)
