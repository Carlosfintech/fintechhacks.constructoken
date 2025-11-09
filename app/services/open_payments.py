"""
Open Payments API Client.
Provides methods for interacting with the Open Payments protocol.
Implements GNAP for authorization and Open Payments APIs for quotes and payments.
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class OpenPaymentsClient:
    """
    Client for interacting with Open Payments APIs.
    Handles authorization (GNAP), quotes, and payment creation.
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_tokens: Dict[str, Dict[str, Any]] = {}  # Cache for access tokens
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    # ========================================================================
    # GNAP (Grant Negotiation and Authorization Protocol)
    # ========================================================================
    
    async def request_grant(
        self,
        auth_server: str,
        wallet_address: str,
        access_type: str,
        amount: Optional[Dict[str, Any]] = None,
        interval: Optional[str] = None,
        iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Request a grant from the authorization server using GNAP.
        
        Args:
            auth_server: URL of the authorization server
            wallet_address: Wallet address requesting the grant
            access_type: Type of access ("outgoing-payment" or "incoming-payment")
            amount: Optional amount limits for the grant
            interval: Optional interval for recurring payments
            iterations: Optional number of iterations for recurring payments
        
        Returns:
            Grant response containing access token and grant ID
        """
        try:
            # Build the access request
            access_request = {
                "type": access_type,
                "actions": ["create", "read", "list"],
                "identifier": wallet_address
            }
            
            # Add limits for outgoing payments
            if access_type == "outgoing-payment" and amount:
                access_request["limits"] = {
                    "debitAmount": amount
                }
                if interval:
                    access_request["limits"]["interval"] = interval
                if iterations:
                    access_request["limits"]["iterations"] = iterations
            
            # Build the grant request
            grant_request = {
                "access_token": {
                    "access": [access_request]
                },
                "client": {
                    "display": {
                        "name": "Constructoken",
                        "uri": "https://constructoken.com"
                    }
                },
                "interact": {
                    "start": ["redirect"],
                    "finish": {
                        "method": "redirect",
                        "uri": "https://constructoken.com/callback",
                        "nonce": self._generate_nonce()
                    }
                }
            }
            
            logger.info(f"Requesting grant from {auth_server}")
            logger.info(f"📤 Grant Request Body: {json.dumps(grant_request, indent=2)}")
            
            response = await self.client.post(
                f"{auth_server}/",
                json=grant_request,
                headers={"Content-Type": "application/json"}
            )
            
            # Log response details before raising error
            logger.info(f"📥 Response Status: {response.status_code}")
            logger.info(f"📥 Response Headers: {dict(response.headers)}")
            try:
                response_body = response.json()
                logger.info(f"📥 Response Body: {json.dumps(response_body, indent=2)}")
            except:
                logger.info(f"📥 Response Text: {response.text}")
            
            response.raise_for_status()
            
            grant_response = response.json()
            logger.info(f"✅ Grant response: {grant_response}")
            
            # Cache the access token if provided
            if "access_token" in grant_response:
                token_value = grant_response["access_token"]["value"]
                self.access_tokens[wallet_address] = {
                    "token": token_value,
                    "expires_at": datetime.utcnow() + timedelta(hours=1)
                }
            
            return grant_response
            
        except httpx.HTTPError as e:
            logger.error(f"Error requesting grant: {e}")
            raise Exception(f"Failed to request grant: {str(e)}")
    
    async def continue_grant(
        self,
        continue_uri: str,
        continue_token: str,
        interact_ref: str
    ) -> Dict[str, Any]:
        """
        Continue a grant request after user interaction.
        
        Args:
            continue_uri: URI to continue the grant
            continue_token: Token for continuing the grant
            interact_ref: Reference from the user interaction
        
        Returns:
            Continued grant response
        """
        try:
            response = await self.client.post(
                continue_uri,
                json={"interact_ref": interact_ref},
                headers={
                    "Authorization": f"GNAP {continue_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error continuing grant: {e}")
            raise Exception(f"Failed to continue grant: {str(e)}")
    
    # ========================================================================
    # Quotes
    # ========================================================================
    
    async def create_quote(
        self,
        resource_server: str,
        access_token: str,
        wallet_address: str,
        receiver_wallet_address: str,
        debit_amount: Optional[Dict[str, Any]] = None,
        receive_amount: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a quote for a payment.
        
        Args:
            resource_server: URL of the resource server
            access_token: Access token for authorization
            wallet_address: Sender's wallet address
            receiver_wallet_address: Receiver's wallet address
            debit_amount: Amount to debit (for fixed send amount)
            receive_amount: Amount to receive (for fixed receive amount)
        
        Returns:
            Quote details including exchange rate and fees
        """
        try:
            quote_request = {
                "walletAddress": wallet_address,
                "receiver": receiver_wallet_address,
                "method": "ilp"
            }
            
            if debit_amount:
                quote_request["debitAmount"] = debit_amount
            if receive_amount:
                quote_request["receiveAmount"] = receive_amount
            
            logger.info(f"Creating quote: {quote_request}")
            response = await self.client.post(
                f"{resource_server}/quotes",
                json=quote_request,
                headers={
                    "Authorization": f"GNAP {access_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            
            quote = response.json()
            logger.info(f"Quote created: {quote}")
            return quote
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating quote: {e}")
            raise Exception(f"Failed to create quote: {str(e)}")
    
    async def get_quote(
        self,
        resource_server: str,
        quote_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get details of an existing quote.
        
        Args:
            resource_server: URL of the resource server
            quote_id: ID of the quote
            access_token: Access token for authorization
        
        Returns:
            Quote details
        """
        try:
            response = await self.client.get(
                f"{resource_server}/quotes/{quote_id}",
                headers={"Authorization": f"GNAP {access_token}"}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting quote: {e}")
            raise Exception(f"Failed to get quote: {str(e)}")
    
    # ========================================================================
    # Outgoing Payments
    # ========================================================================
    
    async def create_outgoing_payment(
        self,
        resource_server: str,
        access_token: str,
        wallet_address: str,
        quote_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an outgoing payment.
        
        Args:
            resource_server: URL of the resource server
            access_token: Access token for authorization
            wallet_address: Sender's wallet address
            quote_id: ID of the quote to use
            metadata: Optional metadata for the payment
        
        Returns:
            Outgoing payment details
        """
        try:
            payment_request = {
                "walletAddress": wallet_address,
                "quoteId": quote_id
            }
            
            if metadata:
                payment_request["metadata"] = metadata
            
            logger.info(f"Creating outgoing payment: {payment_request}")
            response = await self.client.post(
                f"{resource_server}/outgoing-payments",
                json=payment_request,
                headers={
                    "Authorization": f"GNAP {access_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            
            payment = response.json()
            logger.info(f"Outgoing payment created: {payment}")
            return payment
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating outgoing payment: {e}")
            raise Exception(f"Failed to create outgoing payment: {str(e)}")
    
    async def get_outgoing_payment(
        self,
        resource_server: str,
        payment_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Get details of an outgoing payment.
        
        Args:
            resource_server: URL of the resource server
            payment_id: ID of the payment
            access_token: Access token for authorization
        
        Returns:
            Payment details
        """
        try:
            response = await self.client.get(
                f"{resource_server}/outgoing-payments/{payment_id}",
                headers={"Authorization": f"GNAP {access_token}"}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting outgoing payment: {e}")
            raise Exception(f"Failed to get outgoing payment: {str(e)}")
    
    # ========================================================================
    # Incoming Payments
    # ========================================================================
    
    async def create_incoming_payment(
        self,
        resource_server: str,
        access_token: str,
        wallet_address: str,
        incoming_amount: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an incoming payment request.
        
        Args:
            resource_server: URL of the resource server
            access_token: Access token for authorization
            wallet_address: Receiver's wallet address
            incoming_amount: Amount to receive
            metadata: Optional metadata for the payment
        
        Returns:
            Incoming payment details
        """
        try:
            payment_request = {
                "walletAddress": wallet_address,
                "incomingAmount": incoming_amount
            }
            
            if metadata:
                payment_request["metadata"] = metadata
            
            logger.info(f"Creating incoming payment: {payment_request}")
            response = await self.client.post(
                f"{resource_server}/incoming-payments",
                json=payment_request,
                headers={
                    "Authorization": f"GNAP {access_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            
            payment = response.json()
            logger.info(f"Incoming payment created: {payment}")
            return payment
            
        except httpx.HTTPError as e:
            logger.error(f"Error creating incoming payment: {e}")
            raise Exception(f"Failed to create incoming payment: {str(e)}")
    
    async def get_incoming_payment(
        self,
        resource_server: str,
        payment_id: str,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get details of an incoming payment.
        Note: Incoming payments are often publicly readable.
        
        Args:
            resource_server: URL of the resource server
            payment_id: ID of the payment
            access_token: Optional access token for authorization
        
        Returns:
            Payment details
        """
        try:
            headers = {}
            if access_token:
                headers["Authorization"] = f"GNAP {access_token}"
            
            response = await self.client.get(
                f"{resource_server}/incoming-payments/{payment_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting incoming payment: {e}")
            raise Exception(f"Failed to get incoming payment: {str(e)}")
    
    async def complete_incoming_payment(
        self,
        resource_server: str,
        payment_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Complete an incoming payment after funds are received.
        
        Args:
            resource_server: URL of the resource server
            payment_id: ID of the payment
            access_token: Access token for authorization
        
        Returns:
            Completed payment details
        """
        try:
            response = await self.client.post(
                f"{resource_server}/incoming-payments/{payment_id}/complete",
                headers={
                    "Authorization": f"GNAP {access_token}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error completing incoming payment: {e}")
            raise Exception(f"Failed to complete incoming payment: {str(e)}")
    
    # ========================================================================
    # Wallet Addresses
    # ========================================================================
    
    async def get_wallet_address_info(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get information about a wallet address.
        Wallet addresses are publicly discoverable.
        
        Args:
            wallet_address: The wallet address URL
        
        Returns:
            Wallet address information including auth server and asset details
        """
        try:
            response = await self.client.get(
                wallet_address,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Error getting wallet address info: {e}")
            raise Exception(f"Failed to get wallet address info: {str(e)}")
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def _generate_nonce(self) -> str:
        """Generate a random nonce for GNAP interactions."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def create_amount(self, value: str, asset_code: str, asset_scale: int) -> Dict[str, Any]:
        """
        Create an amount object for Open Payments.
        
        Args:
            value: Amount value as a string (e.g., "1000")
            asset_code: Currency code (e.g., "USD", "MXN")
            asset_scale: Number of decimal places (e.g., 2 for cents)
        
        Returns:
            Amount object
        """
        return {
            "value": value,
            "assetCode": asset_code,
            "assetScale": asset_scale
        }

