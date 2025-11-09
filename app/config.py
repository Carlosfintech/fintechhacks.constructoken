"""
Configuration module for the Constructoken Hackathon application.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/constructoken_hackathon"
    
    # FastAPI
    APP_NAME: str = "Constructoken Hackathon"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # US Wallet (USD) - Sender ASE
    US_WALLET_ADDRESS: str
    US_AUTH_SERVER: str
    US_RESOURCE_SERVER: str
    
    # Finsus Wallet (MXN) - Receiver/Sender ASE
    FINSUS_WALLET_ADDRESS: str
    FINSUS_AUTH_SERVER: str
    FINSUS_RESOURCE_SERVER: str
    
    # Merchant Wallet (MXN) - Receiver ASE
    MERCHANT_WALLET_ADDRESS: str
    MERCHANT_AUTH_SERVER: str
    MERCHANT_RESOURCE_SERVER: str
    
    # Payment Configuration
    RECURRING_PAYMENT_INTERVAL: str = "weekly"
    RECURRING_PAYMENT_COUNT: int = 10
    TARGET_AMOUNT_MXN: float = 1000.00
    PAYMENT_AMOUNT_PER_INSTALLMENT_MXN: float = 100.00
    
    # Currency Configuration
    BASE_CURRENCY_USD: str = "USD"
    TARGET_CURRENCY_MXN: str = "MXN"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

