"""Constructoken - Interledger Hackathon Prototype

API endpoints for payment operations.
"""

from fastapi import APIRouter, HTTPException, Query
from ulid import ULID

from app.schemas.payments import (
    RecurringPaymentStartRequest,
    RecurringPaymentStartResponse,
    RecurringPaymentCallbackResponse,
    RecurringPaymentTriggerRequest,
    RecurringPaymentTriggerResponse,
    OneTimePurchaseStartRequest,
    OneTimePurchaseStartResponse,
    OneTimePurchaseCallbackResponse,
)
from app.services.open_payments_service import (
    create_recurring_payment_service,
    create_purchase_service,
)

router = APIRouter()


###################################################################################################
# FASE I: RECURRING PAYMENTS ENDPOINTS
###################################################################################################


@router.post("/recurring/start", response_model=RecurringPaymentStartResponse)
async def start_recurring_payment(request: RecurringPaymentStartRequest):
    """
    Start the recurring payment authorization flow (Fase I).

    This initiates the process for the Migrante to authorize recurring remittances
    from their USD wallet to their FINSUS MXN account.

    Flow:
    1. Client calls this endpoint with payment parameters
    2. Returns a redirect URL for user authorization
    3. User authorizes the payment in their wallet
    4. User is redirected to the callback endpoint

    Example:
        POST /payments/recurring/start
        {
            "debit_amount": "1000",
            "total_cap": "10000",
            "interval": "R/2025-01-01T00:00:00Z/P1W",
            "max_payments": 10
        }
    """
    try:
        service = create_recurring_payment_service()

        redirect_url, grant_id = service.start_recurring_grant_flow(
            debit_amount=request.debit_amount,
            total_cap=request.total_cap,
            interval=request.interval,
            max_payments=request.max_payments,
            redirect_uri_base=f"{service.redirect_uri}",
        )

        return RecurringPaymentStartResponse(redirect_url=redirect_url, grant_id=grant_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start recurring payment flow: {str(e)}")


@router.get("/recurring/callback", response_model=RecurringPaymentCallbackResponse)
async def recurring_payment_callback(
    interact_ref: str = Query(..., description="Interaction reference from auth server"),
    hash: str = Query(..., description="Hash for verification"),
    grant_id: str = Query(..., description="Grant ID from the path parameter"),
):
    """
    Handle the callback after user authorizes recurring payments.

    This endpoint is called by the authorization server after the user approves
    the recurring payment grant.

    Query Parameters:
    - interact_ref: The interaction reference from the auth server
    - hash: Hash to verify the response integrity
    - grant_id: ID of the grant (embedded in the redirect URI)

    Returns:
        Success/failure response with grant details
    """
    try:
        # Parse grant_id from the last part of the redirect URI
        # The redirect URI is in format: {base_uri}/{grant_id}
        grant_ulid = ULID.from_str(grant_id)

        service = create_recurring_payment_service()

        success = service.complete_recurring_grant_flow(
            grant_id=grant_ulid, interact_ref=interact_ref, received_hash=hash
        )

        return RecurringPaymentCallbackResponse(
            success=success,
            message="Recurring payment grant established successfully. You can now execute recurring payments.",
            grant_id=grant_ulid,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete grant flow: {str(e)}")


@router.post("/recurring/trigger", response_model=RecurringPaymentTriggerResponse)
async def trigger_recurring_payment(request: RecurringPaymentTriggerRequest):
    """
    Execute a single recurring payment using an established grant.

    This simulates a scheduled payment execution (e.g., weekly).

    Flow:
    1. Retrieves the active recurring grant
    2. Creates a quote for current exchange rates
    3. Executes the outgoing payment from Migrante to FINSUS

    Example:
        POST /payments/recurring/trigger
        {
            "grant_id": "01HQXYZ..."
        }
    """
    try:
        service = create_recurring_payment_service()

        result = service.execute_recurring_payment(grant_id=request.grant_id)

        return RecurringPaymentTriggerResponse(
            success=True,
            message="Recurring payment executed successfully",
            outgoing_payment_id=result["outgoing_payment_id"],
            quote_debit_amount=result["quote_debit_amount"],
            quote_receive_amount=result["quote_receive_amount"],
            payments_made=result["payments_made"],
            payments_remaining=result["payments_remaining"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute recurring payment: {str(e)}")


###################################################################################################
# FASE II: ONE-TIME PURCHASE ENDPOINTS
###################################################################################################


@router.post("/purchase/start", response_model=OneTimePurchaseStartResponse)
async def start_one_time_purchase(request: OneTimePurchaseStartRequest):
    """
    Start the one-time purchase flow (Fase II).

    This initiates the process for purchasing construction materials from the Merchant
    using funds from the FINSUS account.

    Flow:
    1. Creates an incoming payment on the Merchant wallet
    2. Creates a quote for the payment
    3. Requests an interactive outgoing payment grant from FINSUS wallet
    4. Returns redirect URL for user authorization

    Example:
        POST /payments/purchase/start
        {
            "amount": "100000"
        }

    The amount should be in the smallest unit (e.g., 100000 = $1,000.00 MXN)
    """
    try:
        service = create_purchase_service()

        redirect_url, pending_transaction = service.get_purchase_endpoint(amount=request.amount)

        return OneTimePurchaseStartResponse(
            redirect_url=redirect_url,
            transaction_id=pending_transaction.id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start purchase flow: {str(e)}")


@router.get("/purchase/callback", response_model=OneTimePurchaseCallbackResponse)
async def one_time_purchase_callback(
    interact_ref: str = Query(..., description="Interaction reference from auth server"),
    hash: str = Query(..., description="Hash for verification"),
    transaction_id: str = Query(..., description="Transaction ID from the path parameter"),
):
    """
    Handle the callback after user authorizes one-time purchase.

    This endpoint is called by the authorization server after the user approves
    the payment.

    Query Parameters:
    - interact_ref: The interaction reference from the auth server
    - hash: Hash to verify the response integrity
    - transaction_id: ID of the transaction (embedded in the redirect URI)

    Returns:
        Success/failure response with payment details
    """
    try:
        # Parse transaction_id from the last part of the redirect URI
        transaction_ulid = ULID.from_str(transaction_id)

        service = create_purchase_service()

        outgoing_payment = service.complete_payment(
            transaction_id=transaction_ulid, interact_ref=interact_ref, received_hash=hash
        )

        return OneTimePurchaseCallbackResponse(
            success=True,
            message="Purchase completed successfully",
            transaction_id=transaction_ulid,
            outgoing_payment_id=str(outgoing_payment.id),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete purchase: {str(e)}")


###################################################################################################
# UTILITY ENDPOINTS
###################################################################################################


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "constructoken-payments"}
