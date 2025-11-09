"""Constructoken - Interledger Hackathon Prototype

Utility module for Open Payments SDK configuration.
"""

from app.open_payments_sdk.http import HttpClient
from app.open_payments_sdk.client.client import OpenPaymentsClient
from app.utilities.openpayments import paymentsparser
from app.schemas.openpayments.open_payments import SellerOpenPaymentAccount
from app.core.config import settings


def create_http_client(timeout: float = 10.0) -> HttpClient:
    """Create an HTTP client for Open Payments SDK."""
    return HttpClient(http_timeout=timeout)


def create_op_client(
    wallet_address: str,
    key_id: str,
    private_key: str,
    http_client: HttpClient = None
) -> OpenPaymentsClient:
    """
    Create an OpenPaymentsClient instance.

    Args:
        wallet_address: Wallet address URL
        key_id: Key ID for authentication
        private_key: Private key (will be converted to PEM format)
        http_client: Optional HTTP client (creates one if not provided)

    Returns:
        Configured OpenPaymentsClient instance
    """
    if not http_client:
        http_client = create_http_client()

    # Normalize wallet address and private key
    normalized_wallet = paymentsparser.normalise_wallet_address(wallet_address=wallet_address)
    pem_key = paymentsparser.convert_private_key_to_PEM(private_key=private_key)

    return OpenPaymentsClient(
        keyid=key_id,
        private_key=pem_key,
        client_wallet_address=normalized_wallet,
        http_client=http_client,
    )


def create_seller_account(wallet_address: str, key_id: str, private_key: str) -> SellerOpenPaymentAccount:
    """
    Create a SellerOpenPaymentAccount from credentials.

    Args:
        wallet_address: Wallet address URL
        key_id: Key ID for authentication
        private_key: Private key

    Returns:
        SellerOpenPaymentAccount instance
    """
    return SellerOpenPaymentAccount(
        walletAddressUrl=wallet_address,
        keyId=key_id,
        privateKey=private_key,
    )


# Pre-configured wallet accounts for the hackathon
def get_migrante_wallet() -> SellerOpenPaymentAccount:
    """Get Migrante (Pancho) wallet configuration - USD wallet."""
    return create_seller_account(
        wallet_address=settings.MIGRANTE_WALLET_ADDRESS,
        key_id=settings.MIGRANTE_KEY_ID,
        private_key=settings.MIGRANTE_PRIVATE_KEY,
    )


def get_finsus_wallet() -> SellerOpenPaymentAccount:
    """Get FINSUS (Destinatario) wallet configuration - MXN wallet."""
    return create_seller_account(
        wallet_address=settings.FINSUS_WALLET_ADDRESS,
        key_id=settings.FINSUS_KEY_ID,
        private_key=settings.FINSUS_PRIVATE_KEY,
    )


def get_merchant_wallet() -> SellerOpenPaymentAccount:
    """Get Merchant wallet configuration - MXN wallet."""
    return create_seller_account(
        wallet_address=settings.MERCHANT_WALLET_ADDRESS,
        key_id=settings.MERCHANT_KEY_ID,
        private_key=settings.MERCHANT_PRIVATE_KEY,
    )
