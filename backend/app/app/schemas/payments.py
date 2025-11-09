"""Constructoken - Interledger Hackathon Prototype

Pydantic schemas for payment operations.
"""

from typing import Optional
from pydantic import BaseModel, Field, AnyUrl
from ulid import ULID
from app.open_payments_sdk.models.wallet import WalletAddress


# Re-export the PendingIncomingPaymentTransaction from openpayments schemas
from app.schemas.openpayments.open_payments import PendingIncomingPaymentTransaction


class RecurringPaymentGrant(BaseModel):
    """Stores the grant information for recurring payments."""

    id: ULID = Field(default_factory=ULID, description="Unique identifier for this grant.")
    sender_wallet: str = Field(..., description="Wallet address of the sender (Migrante).")
    receiver_wallet: str = Field(..., description="Wallet address of the receiver (FINSUS).")
    access_token: str = Field(..., description="Access token for making recurring payments.")
    continue_uri: AnyUrl = Field(..., description="URI to continue the grant.")
    debit_amount_value: str = Field(..., description="Debit amount per payment (e.g., '1000' for $10.00).")
    debit_amount_asset_code: str = Field(..., description="Asset code (e.g., 'USD').")
    debit_amount_asset_scale: int = Field(..., description="Asset scale (e.g., 2 for cents).")
    total_amount_cap: str = Field(..., description="Total cap amount (e.g., '10000' for $100.00).")
    interval: str = Field(..., description="Interval for recurring payments (ISO 8601 repeating interval).")
    payments_made: int = Field(default=0, description="Number of payments already executed.")
    max_payments: int = Field(..., description="Maximum number of payments allowed.")


class RecurringPaymentStartRequest(BaseModel):
    """Request to start the recurring payment authorization flow."""

    debit_amount: str = Field(..., description="Amount to debit per payment (e.g., '1000' for $10.00 USD).")
    total_cap: str = Field(..., description="Total cap amount (e.g., '10000' for $100.00 USD).")
    interval: str = Field(
        default="R/2025-01-01T00:00:00Z/P1W",
        description="ISO 8601 repeating interval (e.g., 'R/2025-01-01T00:00:00Z/P1W' for weekly).",
    )
    max_payments: int = Field(default=10, description="Maximum number of payments to execute.")


class RecurringPaymentStartResponse(BaseModel):
    """Response from starting recurring payment flow."""

    redirect_url: str = Field(..., description="URL to redirect the user for authorization.")
    grant_id: ULID = Field(..., description="ID to track this grant request.")


class RecurringPaymentCallbackRequest(BaseModel):
    """Query parameters received in the callback after user authorization."""

    interact_ref: str = Field(..., description="Interaction reference from the authorization server.")
    hash: str = Field(..., description="Hash to verify the response integrity.")


class RecurringPaymentCallbackResponse(BaseModel):
    """Response after processing the recurring payment callback."""

    success: bool = Field(..., description="Whether the grant was successfully established.")
    message: str = Field(..., description="Status message.")
    grant_id: Optional[ULID] = Field(None, description="ID of the established grant.")


class RecurringPaymentTriggerRequest(BaseModel):
    """Request to trigger a single recurring payment."""

    grant_id: ULID = Field(..., description="ID of the recurring payment grant.")


class RecurringPaymentTriggerResponse(BaseModel):
    """Response after triggering a recurring payment."""

    success: bool = Field(..., description="Whether the payment was successful.")
    message: str = Field(..., description="Status message.")
    outgoing_payment_id: Optional[str] = Field(None, description="ID of the created outgoing payment.")
    quote_debit_amount: Optional[str] = Field(None, description="Quoted debit amount.")
    quote_receive_amount: Optional[str] = Field(None, description="Quoted receive amount.")
    payments_made: Optional[int] = Field(None, description="Total payments made so far.")
    payments_remaining: Optional[int] = Field(None, description="Payments remaining.")


class OneTimePurchaseStartRequest(BaseModel):
    """Request to start a one-time purchase flow."""

    amount: str = Field(..., description="Amount in receiver's currency (e.g., '100000' for $1,000.00 MXN).")


class OneTimePurchaseStartResponse(BaseModel):
    """Response from starting one-time purchase flow."""

    redirect_url: str = Field(..., description="URL to redirect the user for authorization.")
    transaction_id: ULID = Field(..., description="ID to track this transaction.")


class OneTimePurchaseCallbackRequest(BaseModel):
    """Query parameters received in the callback after user authorization."""

    interact_ref: str = Field(..., description="Interaction reference from the authorization server.")
    hash: str = Field(..., description="Hash to verify the response integrity.")


class OneTimePurchaseCallbackResponse(BaseModel):
    """Response after processing the one-time purchase callback."""

    success: bool = Field(..., description="Whether the payment was successful.")
    message: str = Field(..., description="Status message.")
    transaction_id: Optional[ULID] = Field(None, description="ID of the completed transaction.")
    outgoing_payment_id: Optional[str] = Field(None, description="ID of the created outgoing payment.")


class PaymentStatusResponse(BaseModel):
    """Response for payment status queries."""

    status: str = Field(..., description="Current status of the payment.")
    details: dict = Field(default_factory=dict, description="Additional details about the payment.")
