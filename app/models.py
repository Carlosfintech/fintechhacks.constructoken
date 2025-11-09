"""
Database models for the Constructoken Hackathon application.
Defines SQLAlchemy ORM models for projects, savings goals, transactions, and payments.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ProjectStatus(str, enum.Enum):
    """Status of a construction project."""
    PLANNING = "planning"
    FUNDING = "funding"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionStatus(str, enum.Enum):
    """Status of a payment transaction."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentType(str, enum.Enum):
    """Type of payment."""
    RECURRING_REMITTANCE = "recurring_remittance"  # USD to MXN recurring
    ONE_TIME_PURCHASE = "one_time_purchase"        # MXN to Merchant


class Migrant(Base):
    """
    Represents a migrant user who sends money from the US.
    """
    __tablename__ = "migrants"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    
    # Wallet addresses
    us_wallet_address = Column(String)  # USD wallet in the US
    finsus_wallet_address = Column(String)  # MXN wallet in Mexico (Finsus)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="migrant")


class Project(Base):
    """
    Represents a construction project divided into stages.
    Each stage becomes a savings goal.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    migrant_id = Column(Integer, ForeignKey("migrants.id"), nullable=False)
    
    # Project details
    name = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)  # Where the construction will take place
    total_budget_mxn = Column(Float, nullable=False)
    
    # Status
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    migrant = relationship("Migrant", back_populates="projects")
    stages = relationship("ProjectStage", back_populates="project")


class ProjectStage(Base):
    """
    Represents a stage of a construction project.
    Each stage is a savings goal that needs to be funded.
    """
    __tablename__ = "project_stages"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Stage details
    name = Column(String, nullable=False)  # e.g., "Foundation", "Walls", "Roof"
    description = Column(Text)
    order = Column(Integer, nullable=False)  # Order in the project sequence
    
    # Financial details
    target_amount_mxn = Column(Float, nullable=False)
    current_amount_mxn = Column(Float, default=0.0)
    
    # Status
    is_funded = Column(Boolean, default=False)
    is_purchased = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    funded_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="stages")
    recurring_payment_setup = relationship(
        "RecurringPaymentSetup", 
        back_populates="stage", 
        uselist=False
    )
    transactions = relationship("Transaction", back_populates="stage")
    purchase = relationship("MaterialPurchase", back_populates="stage", uselist=False)


class RecurringPaymentSetup(Base):
    """
    Stores the configuration for recurring payments (USD to MXN).
    Represents Phase I: Recurring remittances.
    """
    __tablename__ = "recurring_payment_setups"
    
    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("project_stages.id"), nullable=False)
    
    # Open Payments Grant details
    grant_id = Column(String)  # Grant ID from GNAP
    access_token = Column(String)  # Access token for making payments
    
    # Payment configuration
    total_amount_mxn = Column(Float, nullable=False)
    installment_amount_mxn = Column(Float, nullable=False)
    number_of_payments = Column(Integer, nullable=False)
    interval = Column(String, default="weekly")  # weekly, biweekly, monthly
    
    # Wallet addresses
    sender_wallet_address = Column(String, nullable=False)  # US wallet (USD)
    recipient_wallet_address = Column(String, nullable=False)  # Finsus wallet (MXN)
    
    # Open Payments resources
    quote_id = Column(String)  # Quote ID for the recurring payment
    outgoing_payment_id = Column(String)  # Outgoing payment ID
    
    # Status
    is_active = Column(Boolean, default=True)
    payments_completed = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    stage = relationship("ProjectStage", back_populates="recurring_payment_setup")


class Transaction(Base):
    """
    Represents an individual payment transaction.
    Can be either a recurring payment installment or a one-time purchase.
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("project_stages.id"), nullable=False)
    
    # Transaction details
    payment_type = Column(Enum(PaymentType), nullable=False)
    amount_mxn = Column(Float, nullable=False)
    amount_usd = Column(Float, nullable=True)  # For USD transactions
    
    # Wallet addresses
    sender_wallet_address = Column(String, nullable=False)
    recipient_wallet_address = Column(String, nullable=False)
    
    # Open Payments resources
    quote_id = Column(String)
    outgoing_payment_id = Column(String)
    incoming_payment_id = Column(String, nullable=True)  # For one-time purchases
    
    # Status
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    stage = relationship("ProjectStage", back_populates="transactions")


class MaterialPurchase(Base):
    """
    Represents a purchase of materials from a merchant.
    Represents Phase II: One-time payment for purchase.
    """
    __tablename__ = "material_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("project_stages.id"), nullable=False)
    
    # Purchase details
    merchant_name = Column(String, nullable=False)
    items_description = Column(Text)
    total_amount_mxn = Column(Float, nullable=False)
    
    # Wallet addresses
    buyer_wallet_address = Column(String, nullable=False)  # Finsus wallet
    merchant_wallet_address = Column(String, nullable=False)  # Merchant wallet
    
    # Open Payments resources
    incoming_payment_id = Column(String)  # Created by merchant
    quote_id = Column(String)
    outgoing_payment_id = Column(String)  # Created by buyer (Finsus)
    grant_id = Column(String)  # Grant for the outgoing payment
    
    # Status
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Delivery information
    delivery_address = Column(String)
    delivery_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    stage = relationship("ProjectStage", back_populates="purchase")

