#!/usr/bin/env python3
"""Test imports for Constructoken Hackathon code"""

import sys
sys.path.insert(0, '/app')

print('=== Verificando imports del código de Constructoken ===')
print()

try:
    print('1. Verificando utils/open_payments_client.py...')
    from app.utils.open_payments_client import get_migrante_wallet, get_finsus_wallet, get_merchant_wallet
    print('   ✓ Imports correctos')

    print('2. Verificando schemas/payments.py...')
    from app.schemas.payments import RecurringPaymentGrant, OneTimePurchaseStartRequest
    print('   ✓ Schemas correctos')

    print('3. Verificando services/open_payments_service.py...')
    from app.services.open_payments_service import OpenPaymentsService
    print('   ✓ Service importado correctamente')

    print('4. Verificando api/endpoints/payments.py...')
    from app.api.api_v1.endpoints import payments
    print('   ✓ Endpoints importados correctamente')

    print()
    print('=== Verificando configuración de wallets ===')
    from app.core.config import settings
    print(f'   Migrante: {settings.MIGRANTE_WALLET_ADDRESS}')
    print(f'   FINSUS: {settings.FINSUS_WALLET_ADDRESS}')
    print(f'   Merchant: {settings.MERCHANT_WALLET_ADDRESS}')
    print()
    print('✅ TODOS LOS IMPORTS FUNCIONAN CORRECTAMENTE')
    print('✅ El código de Constructoken NO tiene errores de importación')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
