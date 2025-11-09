"""
Main FastAPI application for Constructoken Hackathon.
Implements the Interledger Open Payments integration for cross-border remittances
and material purchases.
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from app.config import settings
from app.database import get_db, init_db
from app.models import (
    Migrant, Project, ProjectStage, RecurringPaymentSetup,
    MaterialPurchase, Transaction, ProjectStatus
)
from app.schemas.payment_schemas import (
    MigrantCreate, MigrantResponse,
    ProjectCreate, ProjectResponse, ProjectStageResponse,
    RecurringPaymentSetupRequest, RecurringPaymentSetupResponse,
    MaterialPurchaseRequest, MaterialPurchaseResponse,
    TransactionResponse, StageStatusResponse, WebhookPaymentEvent
)
from app.services.recurring_payments import RecurringPaymentService
from app.services.one_time_payment import OneTimePaymentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Open Payments integration for Constructoken - Interledger Hackathon",
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Startup and Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup."""
    logger.info("Starting Constructoken Hackathon API")
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Constructoken Hackathon API")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "message": "Constructoken Hackathon - Interledger Open Payments Integration"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "open_payments": "configured"
    }


# ============================================================================
# Migrant Endpoints
# ============================================================================

@app.post("/migrants", response_model=MigrantResponse, tags=["Migrants"])
async def create_migrant(
    migrant: MigrantCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new migrant user.
    
    A migrant is a user who sends money from the US to fund construction projects.
    """
    try:
        # Check if migrant with email already exists
        existing = db.query(Migrant).filter(Migrant.email == migrant.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Migrant with this email already exists")
        
        db_migrant = Migrant(**migrant.model_dump())
        db.add(db_migrant)
        db.commit()
        db.refresh(db_migrant)
        
        logger.info(f"Created migrant: {db_migrant.id} - {db_migrant.email}")
        return db_migrant
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating migrant: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/migrants/{migrant_id}", response_model=MigrantResponse, tags=["Migrants"])
async def get_migrant(
    migrant_id: int,
    db: Session = Depends(get_db)
):
    """Get a migrant by ID."""
    migrant = db.query(Migrant).filter(Migrant.id == migrant_id).first()
    if not migrant:
        raise HTTPException(status_code=404, detail="Migrant not found")
    return migrant


@app.get("/migrants", response_model=List[MigrantResponse], tags=["Migrants"])
async def list_migrants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all migrants."""
    migrants = db.query(Migrant).offset(skip).limit(limit).all()
    return migrants


# ============================================================================
# Project Endpoints
# ============================================================================

@app.post("/projects", response_model=ProjectResponse, tags=["Projects"])
async def create_project(
    migrant_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new construction project with stages.
    
    A project represents a house construction divided into stages.
    Each stage becomes a savings goal that can be funded through recurring payments.
    """
    try:
        # Check if migrant exists
        migrant = db.query(Migrant).filter(Migrant.id == migrant_id).first()
        if not migrant:
            raise HTTPException(status_code=404, detail="Migrant not found")
        
        # Create project
        db_project = Project(
            migrant_id=migrant_id,
            name=project.name,
            description=project.description,
            location=project.location,
            total_budget_mxn=project.total_budget_mxn,
            status=ProjectStatus.PLANNING
        )
        db.add(db_project)
        db.flush()  # Get project ID
        
        # Create stages
        for stage_data in project.stages:
            db_stage = ProjectStage(
                project_id=db_project.id,
                **stage_data.model_dump()
            )
            db.add(db_stage)
        
        db.commit()
        db.refresh(db_project)
        
        logger.info(f"Created project: {db_project.id} with {len(project.stages)} stages")
        return db_project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get a project by ID with all its stages."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/migrants/{migrant_id}/projects", response_model=List[ProjectResponse], tags=["Projects"])
async def list_migrant_projects(
    migrant_id: int,
    db: Session = Depends(get_db)
):
    """List all projects for a specific migrant."""
    projects = db.query(Project).filter(Project.migrant_id == migrant_id).all()
    return projects


@app.get("/stages/{stage_id}", response_model=ProjectStageResponse, tags=["Projects"])
async def get_stage(
    stage_id: int,
    db: Session = Depends(get_db)
):
    """Get a project stage by ID."""
    stage = db.query(ProjectStage).filter(ProjectStage.id == stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    return stage


# ============================================================================
# Phase I: Recurring Payments (USD -> MXN)
# ============================================================================

@app.post(
    "/recurring-payments/setup",
    response_model=RecurringPaymentSetupResponse,
    tags=["Phase I: Recurring Payments"]
)
async def setup_recurring_payment(
    request: RecurringPaymentSetupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Set up recurring payments for a construction stage.
    
    This implements Phase I: Recurring remittances from US wallet (USD) to Finsus wallet (MXN).
    
    Flow:
    1. Request grant from US wallet (GNAP)
    2. Create quote for USD -> MXN conversion
    3. Create recurring outgoing payment instruction
    
    The payments will be executed automatically at the specified interval.
    """
    service = RecurringPaymentService(db)
    
    try:
        # Verify stage exists and is not already funded
        stage = db.query(ProjectStage).filter(ProjectStage.id == request.stage_id).first()
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        
        if stage.is_funded:
            raise HTTPException(status_code=400, detail="Stage is already funded")
        
        # Set up recurring payment
        logger.info(f"Setting up recurring payment for stage {request.stage_id}")
        recurring_setup = await service.setup_recurring_payment(
            stage_id=request.stage_id,
            installment_amount_mxn=request.installment_amount_mxn,
            number_of_payments=request.number_of_payments,
            interval=request.interval
        )
        
        # Update project status to funding
        stage.project.status = ProjectStatus.FUNDING
        db.commit()
        
        logger.info(f"Recurring payment setup completed: {recurring_setup.id}")
        return recurring_setup
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up recurring payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.close()


@app.get(
    "/recurring-payments/{setup_id}/status",
    tags=["Phase I: Recurring Payments"]
)
async def check_recurring_payment_status(
    setup_id: int,
    db: Session = Depends(get_db)
):
    """
    Check the status of a recurring payment setup.
    
    Returns information about payments completed, amount funded, and funding progress.
    """
    service = RecurringPaymentService(db)
    
    try:
        status = await service.check_payment_status(setup_id)
        return status
        
    except Exception as e:
        logger.error(f"Error checking recurring payment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.close()


@app.get(
    "/stages/{stage_id}/funding-status",
    response_model=StageStatusResponse,
    tags=["Phase I: Recurring Payments"]
)
async def get_stage_funding_status(
    stage_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the funding status of a stage.
    
    Returns progress information for the stage's savings goal.
    """
    stage = db.query(ProjectStage).filter(ProjectStage.id == stage_id).first()
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    recurring_setup = db.query(RecurringPaymentSetup).filter(
        RecurringPaymentSetup.stage_id == stage_id
    ).first()
    
    payments_completed = recurring_setup.payments_completed if recurring_setup else 0
    total_payments = recurring_setup.number_of_payments if recurring_setup else 0
    
    funding_progress = (
        (stage.current_amount_mxn / stage.target_amount_mxn * 100)
        if stage.target_amount_mxn > 0 else 0
    )
    
    return StageStatusResponse(
        stage_id=stage.id,
        stage_name=stage.name,
        target_amount_mxn=stage.target_amount_mxn,
        current_amount_mxn=stage.current_amount_mxn,
        is_funded=stage.is_funded,
        is_purchased=stage.is_purchased,
        funding_progress_percentage=funding_progress,
        payments_completed=payments_completed,
        total_payments=total_payments
    )


# ============================================================================
# Phase II: One-Time Purchase (MXN -> Merchant)
# ============================================================================

@app.post(
    "/material-purchases",
    response_model=MaterialPurchaseResponse,
    tags=["Phase II: Material Purchase"]
)
async def purchase_materials(
    request: MaterialPurchaseRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Purchase materials for a funded construction stage.
    
    This implements Phase II: One-time payment from Finsus wallet (MXN) to Merchant wallet (MXN).
    
    Flow:
    1. Verify stage is fully funded
    2. Create incoming payment on merchant's side
    3. Request grant for outgoing payment from Finsus
    4. Create quote for the payment
    5. Execute payment from Finsus to merchant
    
    The stage must be fully funded before materials can be purchased.
    """
    service = OneTimePaymentService(db)
    
    try:
        # Verify stage is funded
        stage = db.query(ProjectStage).filter(ProjectStage.id == request.stage_id).first()
        if not stage:
            raise HTTPException(status_code=404, detail="Stage not found")
        
        if not stage.is_funded:
            raise HTTPException(
                status_code=400,
                detail=f"Stage is not fully funded. Current: {stage.current_amount_mxn} MXN, "
                       f"Target: {stage.target_amount_mxn} MXN"
            )
        
        if stage.is_purchased:
            raise HTTPException(status_code=400, detail="Materials already purchased for this stage")
        
        # Create material purchase
        logger.info(f"Creating material purchase for stage {request.stage_id}")
        purchase = await service.create_material_purchase(
            stage_id=request.stage_id,
            merchant_name=request.merchant_name,
            merchant_wallet_address=request.merchant_wallet_address,
            items_description=request.items_description,
            delivery_address=request.delivery_address,
            delivery_notes=request.delivery_notes
        )
        
        logger.info(f"Material purchase created: {purchase.id}")
        return purchase
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.close()


@app.get(
    "/material-purchases/{purchase_id}/status",
    tags=["Phase II: Material Purchase"]
)
async def check_purchase_status(
    purchase_id: int,
    db: Session = Depends(get_db)
):
    """
    Check the status of a material purchase.
    
    Returns information about the payment status and delivery details.
    """
    service = OneTimePaymentService(db)
    
    try:
        status = await service.check_purchase_status(purchase_id)
        return status
        
    except Exception as e:
        logger.error(f"Error checking purchase status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.close()


@app.get(
    "/material-purchases",
    response_model=List[MaterialPurchaseResponse],
    tags=["Phase II: Material Purchase"]
)
async def list_purchases(
    stage_id: int = None,
    db: Session = Depends(get_db)
):
    """List material purchases, optionally filtered by stage."""
    query = db.query(MaterialPurchase)
    if stage_id:
        query = query.filter(MaterialPurchase.stage_id == stage_id)
    
    purchases = query.all()
    return purchases


# ============================================================================
# Webhooks
# ============================================================================

@app.post("/webhooks/payments", tags=["Webhooks"])
async def payment_webhook(
    event: WebhookPaymentEvent,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Open Payments events.
    
    Receives notifications about payment status changes:
    - outgoing_payment.completed
    - outgoing_payment.failed
    - incoming_payment.completed
    - incoming_payment.failed
    
    This endpoint processes the events and updates the database accordingly.
    """
    try:
        event_type = event.type
        event_data = event.data
        payment_id = event_data.get("id")
        
        logger.info(f"Received webhook: {event_type} for payment {payment_id}")
        
        # Determine if this is a recurring payment or one-time purchase
        if event_type.startswith("outgoing_payment"):
            # Check if it's a recurring payment
            recurring_setup = db.query(RecurringPaymentSetup).filter(
                RecurringPaymentSetup.outgoing_payment_id == payment_id
            ).first()
            
            if recurring_setup:
                # Process recurring payment webhook
                service = RecurringPaymentService(db)
                background_tasks.add_task(
                    service.process_recurring_payment_webhook,
                    payment_id,
                    event_type,
                    event_data
                )
            else:
                # Process one-time purchase webhook
                service = OneTimePaymentService(db)
                background_tasks.add_task(
                    service.process_purchase_webhook,
                    payment_id,
                    event_type,
                    event_data
                )
        
        elif event_type.startswith("incoming_payment"):
            # Process incoming payment webhook (for purchases)
            service = OneTimePaymentService(db)
            background_tasks.add_task(
                service.process_purchase_webhook,
                payment_id,
                event_type,
                event_data
            )
        
        return {"status": "accepted", "message": "Webhook received"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Transactions
# ============================================================================

@app.get("/transactions", response_model=List[TransactionResponse], tags=["Transactions"])
async def list_transactions(
    stage_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all transactions, optionally filtered by stage."""
    query = db.query(Transaction)
    if stage_id:
        query = query.filter(Transaction.stage_id == stage_id)
    
    transactions = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse, tags=["Transactions"])
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


# ============================================================================
# Demo/Testing Endpoints
# ============================================================================

@app.post("/demo/simulate-payment-completion", tags=["Demo"])
async def simulate_payment_completion(
    payment_id: str,
    payment_type: str,  # "recurring" or "one_time"
    db: Session = Depends(get_db)
):
    """
    Simulate a payment completion for testing purposes.
    
    This endpoint simulates a webhook event for testing without actually
    executing payments through Open Payments.
    
    Use this in the sandbox environment to test the full flow.
    """
    try:
        event_type = (
            "outgoing_payment.completed" if payment_type == "recurring"
            else "incoming_payment.completed"
        )
        
        event_data = {
            "id": payment_id,
            "status": "completed"
        }
        
        if payment_type == "recurring":
            service = RecurringPaymentService(db)
            await service.process_recurring_payment_webhook(
                payment_id,
                event_type,
                event_data
            )
        else:
            service = OneTimePaymentService(db)
            await service.process_purchase_webhook(
                payment_id,
                event_type,
                event_data
            )
        
        await service.close()
        
        return {
            "status": "success",
            "message": f"Payment {payment_id} marked as completed"
        }
        
    except Exception as e:
        logger.error(f"Error simulating payment completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

