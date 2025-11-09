"""
One-Time Payment Service (Phase II: MXN -> Merchant).
Implements the "Accept a one-time payment for an online purchase" use case.
Handles the flow from Finsus wallet (MXN) to Merchant wallet (MXN).
"""
from sqlalchemy.orm import Session
from app.models import (
    ProjectStage, MaterialPurchase, Transaction,
    TransactionStatus, PaymentType
)
from app.services.open_payments import OpenPaymentsClient
from app.config import settings
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OneTimePaymentService:
    """
    Service for managing one-time payments for material purchases.
    Implements Phase II: Payment from Finsus wallet (MXN) to Merchant wallet (MXN).
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.op_client = OpenPaymentsClient()
    
    async def create_material_purchase(
        self,
        stage_id: int,
        merchant_name: str,
        merchant_wallet_address: str,
        items_description: str,
        delivery_address: str,
        delivery_notes: str = None
    ) -> MaterialPurchase:
        """
        Create a material purchase using Open Payments.
        
        This implements the complete flow:
        1. Verify stage is fully funded
        2. Create incoming payment on merchant's side
        3. Request grant for outgoing payment from Finsus wallet
        4. Create quote for the payment
        5. Create outgoing payment from Finsus to merchant
        6. Complete the incoming payment
        
        Args:
            stage_id: ID of the funded project stage
            merchant_name: Name of the merchant
            merchant_wallet_address: Merchant's wallet address
            items_description: Description of materials being purchased
            delivery_address: Delivery address for materials
            delivery_notes: Optional delivery notes
        
        Returns:
            MaterialPurchase object with payment details
        """
        try:
            # Step 0: Verify stage is funded
            stage = self.db.query(ProjectStage).filter(
                ProjectStage.id == stage_id
            ).first()
            
            if not stage:
                raise ValueError(f"Stage with ID {stage_id} not found")
            
            if not stage.is_funded:
                raise ValueError(f"Stage {stage_id} is not fully funded yet")
            
            if stage.is_purchased:
                raise ValueError(f"Stage {stage_id} has already been purchased")
            
            # Get migrant and wallet addresses
            migrant = stage.project.migrant
            finsus_wallet = migrant.finsus_wallet_address or settings.FINSUS_WALLET_ADDRESS
            
            purchase_amount_mxn = stage.target_amount_mxn
            
            logger.info(
                f"Creating material purchase for stage {stage_id}: "
                f"{purchase_amount_mxn} MXN to {merchant_name}"
            )
            
            # Step 1: Create Incoming Payment (Merchant Side)
            # The merchant creates an invoice/payment request
            logger.info("Step 1: Creating incoming payment on merchant side")
            
            # First, get grant for merchant to create incoming payment
            merchant_grant = await self.op_client.request_grant(
                auth_server=settings.MERCHANT_AUTH_SERVER,
                wallet_address=merchant_wallet_address,
                access_type="incoming-payment"
            )
            
            merchant_access_token = merchant_grant.get("access_token", {}).get("value")
            
            incoming_amount = self.op_client.create_amount(
                value=str(int(purchase_amount_mxn * 100)),  # Convert to cents
                asset_code=settings.TARGET_CURRENCY_MXN,
                asset_scale=2
            )
            
            incoming_payment_metadata = {
                "description": f"Material purchase for {stage.name}",
                "merchant": merchant_name,
                "stage_id": stage_id,
                "project_id": stage.project.id
            }
            
            incoming_payment = await self.op_client.create_incoming_payment(
                resource_server=settings.MERCHANT_RESOURCE_SERVER,
                access_token=merchant_access_token,
                wallet_address=merchant_wallet_address,
                incoming_amount=incoming_amount,
                metadata=incoming_payment_metadata
            )
            
            incoming_payment_id = incoming_payment.get("id")
            logger.info(f"Incoming payment created: {incoming_payment_id}")
            
            # Step 2: Create Grant for Outgoing Payment (Buyer/Finsus Side)
            # The migrant needs to authorize payment from Finsus wallet
            logger.info("Step 2: Requesting grant from Finsus wallet")
            
            debit_amount = self.op_client.create_amount(
                value=str(int(purchase_amount_mxn * 100)),
                asset_code=settings.TARGET_CURRENCY_MXN,
                asset_scale=2
            )
            
            finsus_grant = await self.op_client.request_grant(
                auth_server=settings.FINSUS_AUTH_SERVER,
                wallet_address=finsus_wallet,
                access_type="outgoing-payment",
                amount=debit_amount
            )
            
            finsus_access_token = finsus_grant.get("access_token", {}).get("value")
            finsus_grant_id = finsus_grant.get("continue", {}).get("access_token", {}).get("value")
            
            if not finsus_access_token:
                raise Exception("Failed to obtain access token from Finsus grant")
            
            logger.info("Grant obtained from Finsus")
            
            # Step 3: Create Quote
            # Get the exact amount to transfer (including any fees)
            logger.info("Step 3: Creating quote for MXN -> MXN payment")
            
            quote = await self.op_client.create_quote(
                resource_server=settings.FINSUS_RESOURCE_SERVER,
                access_token=finsus_access_token,
                wallet_address=finsus_wallet,
                receiver_wallet_address=merchant_wallet_address,
                receive_amount=incoming_amount  # Ensure merchant receives exact amount
            )
            
            quote_id = quote.get("id")
            logger.info(f"Quote created: {quote_id}")
            
            # Step 4: Create Outgoing Payment from Finsus
            # Execute the payment from Finsus to merchant
            logger.info("Step 4: Creating outgoing payment from Finsus")
            
            outgoing_payment_metadata = {
                "description": f"Payment for {merchant_name} - {items_description}",
                "stage_id": stage_id,
                "incoming_payment_id": incoming_payment_id
            }
            
            outgoing_payment = await self.op_client.create_outgoing_payment(
                resource_server=settings.FINSUS_RESOURCE_SERVER,
                access_token=finsus_access_token,
                wallet_address=finsus_wallet,
                quote_id=quote_id,
                metadata=outgoing_payment_metadata
            )
            
            outgoing_payment_id = outgoing_payment.get("id")
            logger.info(f"Outgoing payment created: {outgoing_payment_id}")
            
            # Step 5: Save to database
            material_purchase = MaterialPurchase(
                stage_id=stage_id,
                merchant_name=merchant_name,
                items_description=items_description,
                total_amount_mxn=purchase_amount_mxn,
                buyer_wallet_address=finsus_wallet,
                merchant_wallet_address=merchant_wallet_address,
                incoming_payment_id=incoming_payment_id,
                quote_id=quote_id,
                outgoing_payment_id=outgoing_payment_id,
                grant_id=finsus_grant_id,
                status=TransactionStatus.PROCESSING,
                delivery_address=delivery_address,
                delivery_notes=delivery_notes
            )
            
            self.db.add(material_purchase)
            
            # Create transaction record
            transaction = Transaction(
                stage_id=stage_id,
                payment_type=PaymentType.ONE_TIME_PURCHASE,
                amount_mxn=purchase_amount_mxn,
                sender_wallet_address=finsus_wallet,
                recipient_wallet_address=merchant_wallet_address,
                quote_id=quote_id,
                outgoing_payment_id=outgoing_payment_id,
                incoming_payment_id=incoming_payment_id,
                status=TransactionStatus.PROCESSING
            )
            
            self.db.add(transaction)
            
            # Mark stage as purchased (pending completion)
            stage.is_purchased = True
            
            self.db.commit()
            self.db.refresh(material_purchase)
            
            logger.info(f"Material purchase created with ID: {material_purchase.id}")
            
            # Note: The incoming payment will be completed via webhook
            # when the merchant receives the funds
            
            return material_purchase
            
        except Exception as e:
            logger.error(f"Error creating material purchase: {e}")
            self.db.rollback()
            raise
    
    async def process_purchase_webhook(
        self,
        payment_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Process webhook notifications for purchase payment events.
        
        Args:
            payment_id: ID of the payment (incoming or outgoing)
            event_type: Type of event
            event_data: Event data from the webhook
        """
        try:
            logger.info(f"Processing purchase webhook for {payment_id}: {event_type}")
            
            # Find the material purchase
            purchase = self.db.query(MaterialPurchase).filter(
                (MaterialPurchase.outgoing_payment_id == payment_id) |
                (MaterialPurchase.incoming_payment_id == payment_id)
            ).first()
            
            if not purchase:
                logger.warning(f"No purchase found for payment {payment_id}")
                return
            
            # Find the transaction
            transaction = self.db.query(Transaction).filter(
                (Transaction.outgoing_payment_id == payment_id) |
                (Transaction.incoming_payment_id == payment_id)
            ).first()
            
            if event_type in ["outgoing_payment.completed", "incoming_payment.completed"]:
                # Payment completed successfully
                purchase.status = TransactionStatus.COMPLETED
                purchase.completed_at = datetime.utcnow()
                
                if transaction:
                    transaction.status = TransactionStatus.COMPLETED
                    transaction.completed_at = datetime.utcnow()
                
                logger.info(f"Material purchase {purchase.id} completed successfully")
                
            elif event_type in ["outgoing_payment.failed", "incoming_payment.failed"]:
                # Payment failed
                error_msg = event_data.get("error", "Payment failed")
                purchase.status = TransactionStatus.FAILED
                purchase.error_message = error_msg
                
                if transaction:
                    transaction.status = TransactionStatus.FAILED
                    transaction.error_message = error_msg
                
                # Revert stage purchase status
                stage = purchase.stage
                stage.is_purchased = False
                
                logger.error(f"Material purchase {purchase.id} failed: {error_msg}")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing purchase webhook: {e}")
            self.db.rollback()
            raise
    
    async def check_purchase_status(
        self,
        purchase_id: int
    ) -> Dict[str, Any]:
        """
        Check the status of a material purchase.
        
        Args:
            purchase_id: ID of the material purchase
        
        Returns:
            Status information
        """
        try:
            purchase = self.db.query(MaterialPurchase).filter(
                MaterialPurchase.id == purchase_id
            ).first()
            
            if not purchase:
                raise ValueError(f"Purchase {purchase_id} not found")
            
            # Get payment status from Open Payments
            outgoing_status = await self.op_client.get_outgoing_payment(
                resource_server=settings.FINSUS_RESOURCE_SERVER,
                payment_id=purchase.outgoing_payment_id,
                access_token=purchase.grant_id  # Using grant_id as access token
            )
            
            incoming_status = await self.op_client.get_incoming_payment(
                resource_server=settings.MERCHANT_RESOURCE_SERVER,
                payment_id=purchase.incoming_payment_id
            )
            
            return {
                "purchase_id": purchase_id,
                "stage_id": purchase.stage_id,
                "merchant_name": purchase.merchant_name,
                "amount_mxn": purchase.total_amount_mxn,
                "status": purchase.status,
                "delivery_address": purchase.delivery_address,
                "created_at": purchase.created_at,
                "completed_at": purchase.completed_at,
                "outgoing_payment_status": outgoing_status,
                "incoming_payment_status": incoming_status
            }
            
        except Exception as e:
            logger.error(f"Error checking purchase status: {e}")
            raise
    
    async def close(self):
        """Close the Open Payments client."""
        await self.op_client.close()

