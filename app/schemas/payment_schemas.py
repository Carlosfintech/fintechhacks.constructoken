"""
Pydantic schemas for payment-related requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProjectStatusEnum(str, Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    FUNDING = "funding"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionStatusEnum(str, Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentTypeEnum(str, Enum):
    """Payment type enumeration."""
    RECURRING_REMITTANCE = "recurring_remittance"
    ONE_TIME_PURCHASE = "one_time_purchase"


# ============================================================================
# Migrant Schemas
# ============================================================================

class MigrantCreate(BaseModel):
    """Schema for creating a new migrant."""
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    us_wallet_address: str
    finsus_wallet_address: str


class MigrantResponse(BaseModel):
    """Schema for migrant response."""
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    us_wallet_address: Optional[str]
    finsus_wallet_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Project Schemas
# ============================================================================

class ProjectStageCreate(BaseModel):
    """Schema for creating a project stage."""
    name: str
    description: Optional[str] = None
    order: int
    target_amount_mxn: float = Field(gt=0)


class ProjectCreate(BaseModel):
    """Schema for creating a new construction project."""
    name: str
    description: Optional[str] = None
    location: str
    total_budget_mxn: float = Field(gt=0)
    stages: List[ProjectStageCreate]


class ProjectStageResponse(BaseModel):
    """Schema for project stage response."""
    id: int
    name: str
    description: Optional[str]
    order: int
    target_amount_mxn: float
    current_amount_mxn: float
    is_funded: bool
    is_purchased: bool
    created_at: datetime
    funded_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: int
    migrant_id: int
    name: str
    description: Optional[str]
    location: str
    total_budget_mxn: float
    status: ProjectStatusEnum
    created_at: datetime
    stages: List[ProjectStageResponse]
    
    class Config:
        from_attributes = True


# ============================================================================
# Recurring Payment Schemas (Phase I: USD -> MXN)
# ============================================================================

class RecurringPaymentSetupRequest(BaseModel):
    """Request to set up recurring payments for a stage."""
    stage_id: int
    installment_amount_mxn: float = Field(gt=0)
    number_of_payments: int = Field(gt=0)
    interval: str = "weekly"  # weekly, biweekly, monthly


class RecurringPaymentSetupResponse(BaseModel):
    """Response after setting up recurring payments."""
    id: int
    stage_id: int
    total_amount_mxn: float
    installment_amount_mxn: float
    number_of_payments: int
    interval: str
    sender_wallet_address: str
    recipient_wallet_address: str
    grant_id: Optional[str]
    quote_id: Optional[str]
    outgoing_payment_id: Optional[str]
    is_active: bool
    payments_completed: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionResponse(BaseModel):
    """Response for a transaction."""
    id: int
    stage_id: int
    payment_type: PaymentTypeEnum
    amount_mxn: float
    amount_usd: Optional[float]
    sender_wallet_address: str
    recipient_wallet_address: str
    status: TransactionStatusEnum
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# Material Purchase Schemas (Phase II: MXN -> Merchant)
# ============================================================================

class MaterialPurchaseRequest(BaseModel):
    """Request to purchase materials for a stage."""
    stage_id: int
    merchant_name: str
    merchant_wallet_address: str
    items_description: Optional[str] = None
    delivery_address: str
    delivery_notes: Optional[str] = None


class MaterialPurchaseResponse(BaseModel):
    """Response after purchasing materials."""
    id: int
    stage_id: int
    merchant_name: str
    total_amount_mxn: float
    buyer_wallet_address: str
    merchant_wallet_address: str
    incoming_payment_id: Optional[str]
    quote_id: Optional[str]
    outgoing_payment_id: Optional[str]
    status: TransactionStatusEnum
    error_message: Optional[str]
    delivery_address: str
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# Open Payments API Schemas
# ============================================================================

class GrantRequest(BaseModel):
    """Schema for GNAP grant request."""
    access_token: dict
    client: dict
    interact: Optional[dict] = None


class QuoteRequest(BaseModel):
    """Schema for creating a quote."""
    walletAddress: str
    receiver: str
    method: str = "ilp"
    

class QuoteResponse(BaseModel):
    """Schema for quote response."""
    id: str
    walletAddress: str
    receiver: str
    debitAmount: dict
    receiveAmount: dict
    createdAt: str
    expiresAt: str


class OutgoingPaymentRequest(BaseModel):
    """Schema for creating an outgoing payment."""
    walletAddress: str
    quoteId: str
    metadata: Optional[dict] = None


class IncomingPaymentRequest(BaseModel):
    """Schema for creating an incoming payment."""
    walletAddress: str
    incomingAmount: dict
    metadata: Optional[dict] = None


# ============================================================================
# Webhook Schemas
# ============================================================================

class WebhookPaymentEvent(BaseModel):
    """Schema for payment webhook events."""
    type: str
    data: dict


# ============================================================================
# Status Check Schemas
# ============================================================================

class StageStatusResponse(BaseModel):
    """Response for checking stage funding status."""
    stage_id: int
    stage_name: str
    target_amount_mxn: float
    current_amount_mxn: float
    is_funded: bool
    is_purchased: bool
    funding_progress_percentage: float
    payments_completed: int
    total_payments: int
    
    class Config:
        from_attributes = True

