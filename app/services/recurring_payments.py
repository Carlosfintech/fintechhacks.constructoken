"""
Recurring Payment Service (Phase I: USD -> MXN).
Implements the "Send recurring remittances with a fixed debit amount" use case.
Handles the flow from US wallet (USD) to Finsus wallet (MXN).
"""
from sqlalchemy.orm import Session
from app.models import (
    ProjectStage, RecurringPaymentSetup, Transaction,
    TransactionStatus, PaymentType
)
from app.services.open_payments import OpenPaymentsClient
from app.config import settings
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RecurringPaymentService:
    """
    Service for managing recurring payment setup and execution.
    Implements Phase I: Remittances from US wallet (USD) to Finsus wallet (MXN).
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.op_client = OpenPaymentsClient()
    
    async def setup_recurring_payment(
        self,
        stage_id: int,
        installment_amount_mxn: float,
        number_of_payments: int,
        interval: str = "weekly"
    ) -> RecurringPaymentSetup:
        """
        Set up recurring payments for a construction stage.
        
        This implements the complete flow:
        1. Request grant from US wallet auth server (GNAP)
        2. Create quote for USD to MXN conversion
        3. Create recurring outgoing payment instruction
        
        Args:
            stage_id: ID of the project stage to fund
            installment_amount_mxn: Amount per installment in MXN
            number_of_payments: Number of recurring payments
            interval: Payment interval (weekly, biweekly, monthly)
        
        Returns:
            RecurringPaymentSetup object with grant and payment details
        """
        try:
            # Get the project stage
            stage = self.db.query(ProjectStage).filter(
                ProjectStage.id == stage_id
            ).first()
            
            if not stage:
                raise ValueError(f"Stage with ID {stage_id} not found")
            
            # Get migrant and wallet addresses
            migrant = stage.project.migrant
            us_wallet = migrant.us_wallet_address or settings.US_WALLET_ADDRESS
            finsus_wallet = migrant.finsus_wallet_address or settings.FINSUS_WALLET_ADDRESS
            
            total_amount_mxn = installment_amount_mxn * number_of_payments
            
            logger.info(
                f"Setting up recurring payment: "
                f"{number_of_payments} payments of {installment_amount_mxn} MXN "
                f"(total: {total_amount_mxn} MXN)"
            )
            
            # Step 1: Request Grant (GNAP)
            # We need authorization to make recurring outgoing payments from the US wallet
            logger.info("Step 1: Requesting grant from US wallet auth server")
            
            # Create the amount limit for the grant
            # Note: The debit will be in USD, but we're specifying MXN target
            debit_amount = self.op_client.create_amount(
                value=str(int(installment_amount_mxn * 100)),  # Convert to cents
                asset_code=settings.TARGET_CURRENCY_MXN,
                asset_scale=2
            )
            
            grant_response = await self.op_client.request_grant(
                auth_server=settings.US_AUTH_SERVER,
                wallet_address=us_wallet,
                access_type="outgoing-payment",
                amount=debit_amount,
                interval=interval,
                iterations=number_of_payments
            )
            
            # Extract access token and grant ID
            access_token = grant_response.get("access_token", {}).get("value")
            grant_id = grant_response.get("continue", {}).get("access_token", {}).get("value")
            
            if not access_token:
                raise Exception("Failed to obtain access token from grant response")
            
            logger.info(f"Grant obtained: {grant_id}")
            
            # Step 2: Create Quote
            # Get the exchange rate and exact amounts for USD -> MXN
            logger.info("Step 2: Creating quote for USD -> MXN conversion")
            
            receive_amount = self.op_client.create_amount(
                value=str(int(installment_amount_mxn * 100)),
                asset_code=settings.TARGET_CURRENCY_MXN,
                asset_scale=2
            )
            
            quote = await self.op_client.create_quote(
                resource_server=settings.US_RESOURCE_SERVER,
                access_token=access_token,
                wallet_address=us_wallet,
                receiver_wallet_address=finsus_wallet,
                receive_amount=receive_amount  # Fixed receive amount (MXN)
            )
            
            quote_id = quote.get("id")
            logger.info(f"Quote created: {quote_id}")
            logger.info(f"Debit amount (USD): {quote.get('debitAmount')}")
            logger.info(f"Receive amount (MXN): {quote.get('receiveAmount')}")
            
            # Step 3: Create Recurring Outgoing Payment
            # Instruct the US wallet to make recurring payments
            logger.info("Step 3: Creating recurring outgoing payment")
            
            metadata = {
                "description": f"Recurring payment for stage: {stage.name}",
                "stage_id": stage_id,
                "project_id": stage.project.id,
                "migrant_id": migrant.id
            }
            
            outgoing_payment = await self.op_client.create_outgoing_payment(
                resource_server=settings.US_RESOURCE_SERVER,
                access_token=access_token,
                wallet_address=us_wallet,
                quote_id=quote_id,
                metadata=metadata
            )
            
            outgoing_payment_id = outgoing_payment.get("id")
            logger.info(f"Recurring outgoing payment created: {outgoing_payment_id}")
            
            # Step 4: Save to database
            recurring_setup = RecurringPaymentSetup(
                stage_id=stage_id,
                grant_id=grant_id,
                access_token=access_token,
                total_amount_mxn=total_amount_mxn,
                installment_amount_mxn=installment_amount_mxn,
                number_of_payments=number_of_payments,
                interval=interval,
                sender_wallet_address=us_wallet,
                recipient_wallet_address=finsus_wallet,
                quote_id=quote_id,
                outgoing_payment_id=outgoing_payment_id,
                is_active=True,
                payments_completed=0
            )
            
            self.db.add(recurring_setup)
            self.db.commit()
            self.db.refresh(recurring_setup)
            
            logger.info(f"Recurring payment setup saved with ID: {recurring_setup.id}")
            
            return recurring_setup
            
        except Exception as e:
            logger.error(f"Error setting up recurring payment: {e}")
            self.db.rollback()
            raise
    
    async def process_recurring_payment_webhook(
        self,
        payment_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Process webhook notifications for recurring payment events.
        
        This is called when a payment in the recurring series is executed.
        Updates the stage's current amount and creates transaction records.
        
        Args:
            payment_id: ID of the outgoing payment
            event_type: Type of event (e.g., "outgoing_payment.completed")
            event_data: Event data from the webhook
        """
        try:
            logger.info(f"Processing webhook for payment {payment_id}: {event_type}")
            
            # Find the recurring payment setup
            recurring_setup = self.db.query(RecurringPaymentSetup).filter(
                RecurringPaymentSetup.outgoing_payment_id == payment_id
            ).first()
            
            if not recurring_setup:
                logger.warning(f"No recurring setup found for payment {payment_id}")
                return
            
            stage = recurring_setup.stage
            
            if event_type == "outgoing_payment.completed":
                # Payment completed successfully
                amount_mxn = recurring_setup.installment_amount_mxn
                
                # Create transaction record
                transaction = Transaction(
                    stage_id=stage.id,
                    payment_type=PaymentType.RECURRING_REMITTANCE,
                    amount_mxn=amount_mxn,
                    sender_wallet_address=recurring_setup.sender_wallet_address,
                    recipient_wallet_address=recurring_setup.recipient_wallet_address,
                    quote_id=recurring_setup.quote_id,
                    outgoing_payment_id=payment_id,
                    status=TransactionStatus.COMPLETED,
                    completed_at=datetime.utcnow()
                )
                self.db.add(transaction)
                
                # Update stage's current amount
                stage.current_amount_mxn += amount_mxn
                
                # Update recurring setup
                recurring_setup.payments_completed += 1
                
                # Check if funding goal is reached
                if stage.current_amount_mxn >= stage.target_amount_mxn:
                    stage.is_funded = True
                    stage.funded_at = datetime.utcnow()
                    logger.info(f"Stage {stage.id} is now fully funded!")
                
                # Check if all recurring payments are completed
                if recurring_setup.payments_completed >= recurring_setup.number_of_payments:
                    recurring_setup.is_active = False
                    recurring_setup.completed_at = datetime.utcnow()
                    logger.info(f"All recurring payments completed for stage {stage.id}")
                
                self.db.commit()
                logger.info(
                    f"Payment processed: {amount_mxn} MXN added to stage {stage.id}. "
                    f"Progress: {stage.current_amount_mxn}/{stage.target_amount_mxn} MXN"
                )
                
            elif event_type == "outgoing_payment.failed":
                # Payment failed
                logger.error(f"Recurring payment {payment_id} failed")
                
                transaction = Transaction(
                    stage_id=stage.id,
                    payment_type=PaymentType.RECURRING_REMITTANCE,
                    amount_mxn=recurring_setup.installment_amount_mxn,
                    sender_wallet_address=recurring_setup.sender_wallet_address,
                    recipient_wallet_address=recurring_setup.recipient_wallet_address,
                    quote_id=recurring_setup.quote_id,
                    outgoing_payment_id=payment_id,
                    status=TransactionStatus.FAILED,
                    error_message=event_data.get("error", "Payment failed")
                )
                self.db.add(transaction)
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            self.db.rollback()
            raise
    
    async def check_payment_status(
        self,
        recurring_setup_id: int
    ) -> Dict[str, Any]:
        """
        Check the status of a recurring payment setup.
        
        Args:
            recurring_setup_id: ID of the recurring payment setup
        
        Returns:
            Status information
        """
        try:
            recurring_setup = self.db.query(RecurringPaymentSetup).filter(
                RecurringPaymentSetup.id == recurring_setup_id
            ).first()
            
            if not recurring_setup:
                raise ValueError(f"Recurring setup {recurring_setup_id} not found")
            
            # Get the latest payment status from Open Payments
            payment_status = await self.op_client.get_outgoing_payment(
                resource_server=settings.US_RESOURCE_SERVER,
                payment_id=recurring_setup.outgoing_payment_id,
                access_token=recurring_setup.access_token
            )
            
            stage = recurring_setup.stage
            
            return {
                "recurring_setup_id": recurring_setup_id,
                "stage_id": stage.id,
                "stage_name": stage.name,
                "is_active": recurring_setup.is_active,
                "payments_completed": recurring_setup.payments_completed,
                "total_payments": recurring_setup.number_of_payments,
                "current_amount_mxn": stage.current_amount_mxn,
                "target_amount_mxn": stage.target_amount_mxn,
                "is_funded": stage.is_funded,
                "payment_status": payment_status
            }
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            raise
    
    async def close(self):
        """Close the Open Payments client."""
        await self.op_client.close()

