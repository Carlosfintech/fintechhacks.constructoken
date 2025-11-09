"""Constructoken - Interledger Hackathon Prototype

Open Payments service implementing recurring and one-time payment flows.
Based on hop-sauna's OpenPaymentsProcessor logic.
"""

from typing import Dict, Optional
from ulid import ULID
from pydantic import AnyUrl

from app.open_payments_sdk.http import HttpClient
from app.open_payments_sdk.client.client import OpenPaymentsClient
from app.open_payments_sdk.api.auth import GrantRequest, Grant, InteractRef
from app.open_payments_sdk.models.resource import (
    IncomingPaymentRequest,
    OutgoingPaymentRequest,
    OutgoingPayment,
    Quote,
    QuoteRequest,
)
from app.open_payments_sdk.models.wallet import WalletAddress

from app.core.config import settings
from app.utilities.openpayments import paymentsparser
from app.schemas.openpayments.open_payments import SellerOpenPaymentAccount, PendingIncomingPaymentTransaction
from app.schemas.payments import RecurringPaymentGrant
from app.utils.open_payments_client import create_http_client, get_migrante_wallet, get_finsus_wallet, get_merchant_wallet


# In-memory storage for the hackathon prototype (replace with database in production)
pending_recurring_grants: Dict[str, Dict] = {}
active_recurring_grants: Dict[str, RecurringPaymentGrant] = {}
pending_purchase_transactions: Dict[str, PendingIncomingPaymentTransaction] = {}


class OpenPaymentsService:
    """
    Service for processing Open Payments flows.

    Implements both recurring payments (Fase I) and one-time purchases (Fase II).
    Based on hop-sauna's OpenPaymentsProcessor architecture.
    """

    def __init__(
        self,
        *,
        seller: SellerOpenPaymentAccount,
        buyer: str,
        http_client: HttpClient = None,
        redirect_uri: str = settings.DEFAULT_REDIRECT_AFTER_AUTH,
    ) -> None:
        if not http_client:
            http_client = create_http_client()

        self.http_client = http_client
        self.seller = seller
        self.buyer = paymentsparser.normalise_wallet_address(wallet_address=buyer)

        self.client = OpenPaymentsClient(
            keyid=self.seller.keyId,
            private_key=self.seller.privateKey,
            client_wallet_address=self.seller.walletAddressUrl,
            http_client=self.http_client,
        )

        self.seller_wallet = self.client.wallet.get_wallet_address(self.seller.walletAddressUrl)
        self.buyer_wallet = self.client.wallet.get_wallet_address(self.buyer)
        self.redirect_uri = redirect_uri

    ###################################################################################################
    # GENERAL GRANT UTILITY
    ###################################################################################################

    def request_grant(self, *, grant: str, actions: list[str], endpoint: AnyUrl) -> Grant:
        """Request a grant from the authorization server."""
        request = GrantRequest(
            **{
                "access_token": {
                    "access": [
                        {
                            "type": grant,
                            "actions": actions,
                        }
                    ]
                },
                "client": str(self.seller_wallet.id),
            }
        )
        return self.client.grants.post_grant_request(grant_request=request, auth_server_endpoint=str(endpoint))

    ###################################################################################################
    # SELLER INCOMING PAYMENT PROCESS
    ###################################################################################################

    def request_incoming_payment(self, *, amount: int | str):
        """Request an incoming payment to the seller."""
        if isinstance(amount, int):
            amount = str(amount)

        # Request a grant
        grant = self.request_grant(
            grant="incoming-payment",
            actions=["create", "read", "read-all", "complete", "list"],
            endpoint=self.seller_wallet.authServer,
        )
        grant_dict = grant.model_dump(exclude_unset=True, mode="json")
        access_token = grant_dict.get("access_token", {}).get("value")

        # Request an incoming payment
        payment = IncomingPaymentRequest(
            **dict(
                walletAddress=str(self.seller_wallet.id),
                incomingAmount=dict(
                    value=amount,
                    assetCode=self.seller_wallet.assetCode.root,
                    assetScale=self.seller_wallet.assetScale.root,
                ),
            )
        )
        return self.client.incoming_payments.post_create_payment(
            payment=payment, resource_server_endpoint=str(self.seller_wallet.resourceServer), access_token=access_token
        )

    ###################################################################################################
    # BUYER QUOTE REQUEST PROCESS
    ###################################################################################################

    def request_quote(self, *, incoming_payment_id: str | AnyUrl) -> Quote:
        """Request a quote from the buyer's wallet."""
        # Request a grant
        grant = self.request_grant(
            grant="quote", actions=["create", "read", "read-all"], endpoint=self.buyer_wallet.authServer
        )
        grant_dict = grant.model_dump(exclude_unset=True, mode="json")
        access_token = grant_dict.get("access_token", {}).get("value")

        # Request a quote for the payment
        quote = QuoteRequest(
            **dict(
                walletAddress=str(self.buyer_wallet.id),
                receiver=str(incoming_payment_id),
                method="ilp",
            )
        )
        return self.client.quotes.post_create_quote(
            quote=quote, resource_server_endpoint=str(self.buyer_wallet.resourceServer), access_token=access_token
        )

    ###################################################################################################
    # FASE I: RECURRING PAYMENTS
    ###################################################################################################

    def start_recurring_grant_flow(
        self, *, debit_amount: str, total_cap: str, interval: str, max_payments: int, redirect_uri_base: str
    ) -> tuple[str, ULID]:
        """
        Start the recurring payment grant flow (Fase I).

        Returns:
            Tuple of (redirect_url, grant_id)
        """
        grant_id = ULID()
        redirect_uri = f"{redirect_uri_base}{grant_id}"

        # Create client with buyer credentials to request grant on their wallet
        buyer_client = OpenPaymentsClient(
            keyid=settings.MIGRANTE_KEY_ID,
            private_key=settings.MIGRANTE_PRIVATE_KEY,
            client_wallet_address=self.buyer,
            http_client=self.http_client,
        )

        # Request an interactive grant with limits for recurring payments
        grant_request = GrantRequest(
            **dict(
                access_token=dict(
                    access=[
                        dict(
                            identifier=str(self.buyer_wallet.id),
                            type="outgoing-payment",
                            actions=["create", "read", "read-all", "list"],
                            limits=dict(
                                debitAmount=dict(
                                    value=debit_amount,
                                    assetCode=self.buyer_wallet.assetCode.root,
                                    assetScale=self.buyer_wallet.assetScale.root,
                                ),
                                interval=interval,
                                cap=dict(
                                    totalAmount=total_cap,
                                    actions=["create"],
                                ),
                            ),
                        ),
                    ],
                ),
                client=str(self.buyer_wallet.id),
                interact=dict(
                    start=["redirect"],
                    finish=dict(
                        method="redirect",
                        uri=redirect_uri,
                        nonce=str(grant_id),
                    ),
                ),
            )
        )

        # Request the interactive endpoint using buyer's client
        interactive_response = buyer_client.grants.post_grant_request(
            grant_request=grant_request, auth_server_endpoint=str(self.buyer_wallet.authServer)
        )

        # Store pending grant data for callback
        pending_recurring_grants[str(grant_id)] = {
            "grant_id": grant_id,
            "sender_wallet": self.buyer,
            "receiver_wallet": self.seller.walletAddressUrl,
            "debit_amount_value": debit_amount,
            "debit_amount_asset_code": self.buyer_wallet.assetCode.root,
            "debit_amount_asset_scale": self.buyer_wallet.assetScale.root,
            "total_amount_cap": total_cap,
            "interval": interval,
            "max_payments": max_payments,
            "finish_id": interactive_response.root.interact.finish,
            "continue_id": interactive_response.root.cont.access_token.value,
            "continue_uri": interactive_response.root.cont.uri,
            "auth_server_url": str(self.buyer_wallet.authServer),
        }

        return interactive_response.root.interact.redirect, grant_id

    def complete_recurring_grant_flow(self, *, grant_id: ULID, interact_ref: str, received_hash: str) -> bool:
        """
        Complete the recurring payment grant flow after user authorization.

        Returns:
            True if successful, raises exception otherwise
        """
        grant_id_str = str(grant_id)

        if grant_id_str not in pending_recurring_grants:
            raise ValueError(f"Grant {grant_id} not found in pending grants")

        pending_data = pending_recurring_grants[grant_id_str]

        # Validate the hash
        if not paymentsparser.verify_response_hash(
            incoming_payment_id=grant_id_str,
            finish_id=pending_data["finish_id"],
            interact_ref=interact_ref,
            auth_server_url=pending_data["auth_server_url"],
            received_hash=received_hash,
        ):
            raise ValueError(f"Hash validation failed for grant {grant_id}")

        # Create buyer client for grant continuation
        buyer_client = OpenPaymentsClient(
            keyid=settings.MIGRANTE_KEY_ID,
            private_key=settings.MIGRANTE_PRIVATE_KEY,
            client_wallet_address=pending_data["sender_wallet"],
            http_client=self.http_client,
        )

        # Request grant continuation
        grant_continuation = buyer_client.grants.post_grant_continuation_request(
            interact_ref=InteractRef(**dict(interact_ref=interact_ref)),
            continue_uri=str(pending_data["continue_uri"]),
            access_token=pending_data["continue_id"],
        )

        # Store the active grant
        active_grant = RecurringPaymentGrant(
            id=grant_id,
            sender_wallet=pending_data["sender_wallet"],
            receiver_wallet=pending_data["receiver_wallet"],
            access_token=grant_continuation.access_token.value,
            continue_uri=pending_data["continue_uri"],
            debit_amount_value=pending_data["debit_amount_value"],
            debit_amount_asset_code=pending_data["debit_amount_asset_code"],
            debit_amount_asset_scale=pending_data["debit_amount_asset_scale"],
            total_amount_cap=pending_data["total_amount_cap"],
            interval=pending_data["interval"],
            payments_made=0,
            max_payments=pending_data["max_payments"],
        )

        active_recurring_grants[grant_id_str] = active_grant

        # Clean up pending grant
        del pending_recurring_grants[grant_id_str]

        return True

    def execute_recurring_payment(self, *, grant_id: ULID) -> Dict:
        """
        Execute a single recurring payment using an established grant.

        Returns:
            Dictionary with payment details
        """
        grant_id_str = str(grant_id)

        if grant_id_str not in active_recurring_grants:
            raise ValueError(f"Active grant {grant_id} not found")

        grant = active_recurring_grants[grant_id_str]

        # Check if we've reached the max payments
        if grant.payments_made >= grant.max_payments:
            raise ValueError(f"Grant {grant_id} has reached maximum payments ({grant.max_payments})")

        # Create an incoming payment on the receiver's wallet (FINSUS)
        receiver_account = SellerOpenPaymentAccount(
            walletAddressUrl=grant.receiver_wallet,
            keyId=settings.FINSUS_KEY_ID,
            privateKey=settings.FINSUS_PRIVATE_KEY,
        )

        receiver_client = OpenPaymentsClient(
            keyid=receiver_account.keyId,
            private_key=receiver_account.privateKey,
            client_wallet_address=receiver_account.walletAddressUrl,
            http_client=self.http_client,
        )

        receiver_wallet = receiver_client.wallet.get_wallet_address(receiver_account.walletAddressUrl)

        # Request incoming payment grant
        incoming_grant = receiver_client.grants.post_grant_request(
            grant_request=GrantRequest(
                **{
                    "access_token": {
                        "access": [
                            {
                                "type": "incoming-payment",
                                "actions": ["create", "read"],
                            }
                        ]
                    },
                    "client": str(receiver_wallet.id),
                }
            ),
            auth_server_endpoint=str(receiver_wallet.authServer),
        )
        incoming_grant_dict = incoming_grant.model_dump(exclude_unset=True, mode="json")
        incoming_access_token = incoming_grant_dict.get("access_token", {}).get("value")

        # Create incoming payment with fixed receiving amount
        # According to Open Payments recurring subscription pattern:
        # 1. Create incoming payment with the amount the receiver expects (in their currency)
        # 2. Create quote to determine how much sender will be debited
        # 3. Create outgoing payment using the recurring grant
        #
        # For cross-currency: USD -> MXN
        # Estimate exchange rate: ~20 MXN/USD
        # $10 USD (1000 cents) -> ~$200 MXN (20000 centavos)
        estimated_receive_amount_mxn = str(int(grant.debit_amount_value) * 20)

        incoming_payment = IncomingPaymentRequest(
            walletAddress=str(receiver_wallet.id),
            incomingAmount=dict(
                value=estimated_receive_amount_mxn,
                assetCode=receiver_wallet.assetCode.root,
                assetScale=receiver_wallet.assetScale.root,
            ),
        )
        incoming_payment_response = receiver_client.incoming_payments.post_create_payment(
            payment=incoming_payment,
            resource_server_endpoint=str(receiver_wallet.resourceServer),
            access_token=incoming_access_token,
        )

        # Request a quote from the sender's wallet
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[DEBUG] grant.sender_wallet: {grant.sender_wallet}")
        logger.error(f"[DEBUG] grant.receiver_wallet: {grant.receiver_wallet}")

        sender_client = OpenPaymentsClient(
            keyid=settings.MIGRANTE_KEY_ID,
            private_key=settings.MIGRANTE_PRIVATE_KEY,
            client_wallet_address=grant.sender_wallet,
            http_client=self.http_client,
        )

        sender_wallet = sender_client.wallet.get_wallet_address(grant.sender_wallet)
        logger.error(f"[DEBUG] sender_wallet.id: {sender_wallet.id}")
        logger.error(f"[DEBUG] sender_wallet.resourceServer: {sender_wallet.resourceServer}")

        quote_grant = sender_client.grants.post_grant_request(
            grant_request=GrantRequest(
                **{
                    "access_token": {
                        "access": [
                            {
                                "type": "quote",
                                "actions": ["create", "read"],
                            }
                        ]
                    },
                    "client": str(sender_wallet.id),
                }
            ),
            auth_server_endpoint=str(sender_wallet.authServer),
        )
        quote_grant_dict = quote_grant.model_dump(exclude_unset=True, mode="json")
        quote_access_token = quote_grant_dict.get("access_token", {}).get("value")

        quote_request = QuoteRequest(
            **dict(
                walletAddress=str(sender_wallet.id),
                receiver=str(incoming_payment_response.id),
                method="ilp",
            )
        )
        quote_response = sender_client.quotes.post_create_quote(
            quote=quote_request, resource_server_endpoint=str(sender_wallet.resourceServer), access_token=quote_access_token
        )

        # Create outgoing payment using the recurring grant token
        outgoing_payment_request = OutgoingPaymentRequest(
            **dict(walletAddress=str(sender_wallet.id), quoteId=quote_response.id, metadata={})
        )
        outgoing_payment = sender_client.outgoing_payments.post_create_payment(
            payment=outgoing_payment_request,
            resource_server_endpoint=str(sender_wallet.resourceServer),
            access_token=grant.access_token,
        )

        # Update payments made counter
        grant.payments_made += 1
        active_recurring_grants[grant_id_str] = grant

        return {
            "outgoing_payment_id": str(outgoing_payment.id),
            "quote_debit_amount": f"{quote_response.debitAmount.value} {quote_response.debitAmount.assetCode}",
            "quote_receive_amount": f"{quote_response.receiveAmount.value} {quote_response.receiveAmount.assetCode}",
            "payments_made": grant.payments_made,
            "payments_remaining": grant.max_payments - grant.payments_made,
        }

    ###################################################################################################
    # FASE II: ONE-TIME PURCHASE
    ###################################################################################################

    def get_purchase_endpoint(self, *, amount: int | str) -> tuple[str, PendingIncomingPaymentTransaction]:
        """
        Start the one-time purchase flow (Fase II).

        Implements the flow from hop-sauna's get_purchase_endpoint method.

        Returns:
            Tuple of (redirect_url, pending_transaction)
        """
        if isinstance(amount, int):
            amount = str(amount)

        # Create pending transaction
        pending_payment = PendingIncomingPaymentTransaction(
            **{"id": ULID(), "seller": self.seller_wallet, "buyer": self.buyer_wallet}
        )
        redirect_uri = f"{self.redirect_uri}{pending_payment.id}"

        # 1. Request incoming payment grant for the seller (merchant)
        incoming_payment_response = self.request_incoming_payment(amount=amount)
        pending_payment.incoming_payment_id = incoming_payment_response.id

        # 2. Request quote grant for the buyer (FINSUS)
        quote_response = self.request_quote(incoming_payment_id=incoming_payment_response.id)
        pending_payment.quote_id = quote_response.id

        # 3. Request an interactive payment endpoint for the buyer
        grant_request = GrantRequest(
            **dict(
                access_token=dict(
                    access=[
                        dict(
                            identifier=str(self.buyer_wallet.id),
                            type="outgoing-payment",
                            actions=["create", "read", "read-all", "list", "list-all"],
                            limits=dict(
                                debitAmount=dict(
                                    assetCode=quote_response.debitAmount.assetCode.root,
                                    assetScale=quote_response.debitAmount.assetScale.root,
                                    value=quote_response.debitAmount.value,
                                ),
                            ),
                        ),
                    ],
                ),
                client=str(self.seller_wallet.id),
                interact=dict(
                    start=["redirect"],
                    finish=dict(
                        method="redirect",
                        uri=redirect_uri,
                        nonce=str(pending_payment.id),
                    ),
                ),
            )
        )

        # Request the interactive endpoint
        interactive_response = self.client.grants.post_grant_request(
            grant_request=grant_request, auth_server_endpoint=str(self.buyer_wallet.authServer)
        )

        pending_payment.interactive_redirect = interactive_response.root.interact.redirect
        pending_payment.finish_id = interactive_response.root.interact.finish
        pending_payment.continue_id = interactive_response.root.cont.access_token.value
        pending_payment.continue_url = interactive_response.root.cont.uri

        # Store pending transaction
        pending_purchase_transactions[str(pending_payment.id)] = pending_payment

        return interactive_response.root.interact.redirect, pending_payment

    def complete_payment(self, *, transaction_id: ULID, interact_ref: str, received_hash: str) -> OutgoingPayment:
        """
        Complete the one-time purchase after user authorization.

        Implements the flow from hop-sauna's complete_payment method.

        Returns:
            OutgoingPayment object
        """
        transaction_id_str = str(transaction_id)

        if transaction_id_str not in pending_purchase_transactions:
            raise ValueError(f"Transaction {transaction_id} not found in pending transactions")

        pending_payment = pending_purchase_transactions[transaction_id_str]

        # Validate the interactive response hash
        if not paymentsparser.verify_response_hash(
            incoming_payment_id=str(pending_payment.id),
            finish_id=pending_payment.finish_id,
            interact_ref=interact_ref,
            auth_server_url=str(pending_payment.buyer.authServer),
            received_hash=received_hash,
        ):
            raise ValueError(f"Hash invalid for pending payment `{pending_payment.incoming_payment_id}`")

        # Request a grant continuation
        grant_request = self.client.grants.post_grant_continuation_request(
            interact_ref=InteractRef(**dict(interact_ref=interact_ref)),
            continue_uri=str(pending_payment.continue_url),
            access_token=pending_payment.continue_id,
        )
        access_token = grant_request.access_token.value

        # Create an outgoing payment from the buyer
        outgoing_payment_request = OutgoingPaymentRequest(
            **dict(walletAddress=str(pending_payment.buyer.id), quoteId=pending_payment.quote_id, metadata={})
        )
        outgoing_payment = self.client.outgoing_payments.post_create_payment(
            payment=outgoing_payment_request,
            resource_server_endpoint=str(pending_payment.buyer.resourceServer),
            access_token=access_token,
        )

        # Clean up pending transaction
        del pending_purchase_transactions[transaction_id_str]

        return outgoing_payment


    ###################################################################################################
    # FASE I: ONE-TIME MIGRANTE PAYMENT (MIGRANTE USD -> FINSUS MXN)
    ###################################################################################################

    def get_migrante_payment_endpoint(self, *, amount: int | str) -> tuple[str, PendingIncomingPaymentTransaction]:
        """
        Start the one-time payment flow for MIGRANTE -> FINSUS (Fase I).
        
        Same pattern as get_purchase_endpoint but for MIGRANTE (USD) -> FINSUS (MXN).
        
        Returns:
            Tuple of (redirect_url, pending_transaction)
        """
        if isinstance(amount, int):
            amount = str(amount)

        # Create pending transaction
        pending_payment = PendingIncomingPaymentTransaction(
            **{"id": ULID(), "seller": self.seller_wallet, "buyer": self.buyer_wallet}
        )
        redirect_uri = f"{self.redirect_uri}{pending_payment.id}"

        # 1. Request incoming payment grant for FINSUS (seller/receiver)
        incoming_payment_response = self.request_incoming_payment(amount=amount)
        pending_payment.incoming_payment_id = incoming_payment_response.id

        # 2. Request quote grant for MIGRANTE (buyer/sender)
        quote_response = self.request_quote(incoming_payment_id=incoming_payment_response.id)
        pending_payment.quote_id = quote_response.id

        # 3. Request an interactive payment endpoint for MIGRANTE
        grant_request = GrantRequest(
            **dict(
                access_token=dict(
                    access=[
                        dict(
                            identifier=str(self.buyer_wallet.id),
                            type="outgoing-payment",
                            actions=["create", "read", "read-all", "list", "list-all"],
                            limits=dict(
                                debitAmount=dict(
                                    assetCode=quote_response.debitAmount.assetCode.root,
                                    assetScale=quote_response.debitAmount.assetScale.root,
                                    value=quote_response.debitAmount.value,
                                ),
                            ),
                        ),
                    ],
                ),
                client=str(self.seller_wallet.id),
                interact=dict(
                    start=["redirect"],
                    finish=dict(
                        method="redirect",
                        uri=redirect_uri,
                        nonce=str(pending_payment.id),
                    ),
                ),
            )
        )

        # Request the interactive endpoint
        interactive_response = self.client.grants.post_grant_request(
            grant_request=grant_request, auth_server_endpoint=str(self.buyer_wallet.authServer)
        )

        pending_payment.interactive_redirect = interactive_response.root.interact.redirect
        pending_payment.finish_id = interactive_response.root.interact.finish
        pending_payment.continue_id = interactive_response.root.cont.access_token.value
        pending_payment.continue_url = interactive_response.root.cont.uri

        # Store pending transaction
        pending_purchase_transactions[str(pending_payment.id)] = pending_payment

        return interactive_response.root.interact.redirect, pending_payment

    def complete_migrante_payment(
        self, *, transaction_id: ULID, interact_ref: str, received_hash: str
    ) -> OutgoingPayment:
        """
        Complete the MIGRANTE -> FINSUS payment after user authorization (Fase I).
        
        Same pattern as complete_payment.
        
        Returns:
            OutgoingPayment object
        """
        transaction_id_str = str(transaction_id)

        if transaction_id_str not in pending_purchase_transactions:
            raise ValueError(f"Transaction {transaction_id} not found in pending transactions")

        pending_payment = pending_purchase_transactions[transaction_id_str]

        # Validate the interactive response hash
        if not paymentsparser.verify_response_hash(
            incoming_payment_id=str(pending_payment.id),
            finish_id=pending_payment.finish_id,
            interact_ref=interact_ref,
            auth_server_url=str(pending_payment.buyer.authServer),
            received_hash=received_hash,
        ):
            raise ValueError(f"Hash invalid for pending payment `{pending_payment.incoming_payment_id}`")

        # Request a grant continuation
        grant_request = self.client.grants.post_grant_continuation_request(
            interact_ref=InteractRef(**dict(interact_ref=interact_ref)),
            continue_uri=str(pending_payment.continue_url),
            access_token=pending_payment.continue_id,
        )
        access_token = grant_request.access_token.value

        # Create an outgoing payment from MIGRANTE
        outgoing_payment_request = OutgoingPaymentRequest(
            **dict(walletAddress=str(pending_payment.buyer.id), quoteId=pending_payment.quote_id, metadata={})
        )
        outgoing_payment = self.client.outgoing_payments.post_create_payment(
            payment=outgoing_payment_request,
            resource_server_endpoint=str(pending_payment.buyer.resourceServer),
            access_token=access_token,
        )

        # Clean up pending transaction
        del pending_purchase_transactions[transaction_id_str]

        return outgoing_payment


###################################################################################################
# HELPER FUNCTIONS FOR CREATING SERVICE INSTANCES
###################################################################################################


def create_migrante_payment_service() -> OpenPaymentsService:
    """
    Create service for one-time MIGRANTE payments (MIGRANTE -> FINSUS).

    Seller = FINSUS (receiver), Buyer = MIGRANTE (sender)
    USD -> MXN conversion
    """
    return OpenPaymentsService(
        seller=get_finsus_wallet(),
        buyer=settings.MIGRANTE_WALLET_ADDRESS,
        redirect_uri=f"{settings.DEFAULT_REDIRECT_AFTER_AUTH}migrante/",
    )


def create_recurring_payment_service() -> OpenPaymentsService:
    """
    Create service for recurring payments (Migrante -> FINSUS) - LEGACY.

    Seller = FINSUS (receiver), Buyer = Migrante (sender)
    """
    return OpenPaymentsService(
        seller=get_finsus_wallet(),
        buyer=settings.MIGRANTE_WALLET_ADDRESS,
        redirect_uri=f"{settings.DEFAULT_REDIRECT_AFTER_AUTH}recurring/",
    )


def create_purchase_service() -> OpenPaymentsService:
    """
    Create service for one-time purchases (FINSUS -> Merchant).

    Seller = Merchant (receiver), Buyer = FINSUS (sender)
    """
    return OpenPaymentsService(
        seller=get_merchant_wallet(),
        buyer=settings.FINSUS_WALLET_ADDRESS,
        redirect_uri=f"{settings.DEFAULT_REDIRECT_AFTER_AUTH}purchase/",
    )
