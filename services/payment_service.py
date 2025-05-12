# app/services/payment_service.py
import requests
from fastapi import HTTPException
from config import settings
import logging

logger = logging.getLogger(__name__)

class PaystackService:
    BASE_URL = "https://api.paystack.co"

    @staticmethod
    async def initialize_transaction(email: str, amount: float, ticket_id: str, callback_url: str) -> dict:
        """
        Initialize a Paystack transaction.
        Amount is in NGN (kobo), so multiply by 100.
        """
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": int(amount * 100),  # Convert to kobo
            "reference": ticket_id,  # Use ticket_id as unique reference
            "callback_url": callback_url,
            "metadata": {"ticket_id": ticket_id}
        }
        try:
            response = requests.post(
                f"{PaystackService.BASE_URL}/transaction/initialize",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("status"):
                logger.error(f"Paystack initialization failed: {data.get('message')}")
                raise HTTPException(status_code=500, detail="Failed to initialize transaction")
            logger.info(f"Transaction initialized for ticket {ticket_id}: {data['data']['authorization_url']}")
            return data["data"]
        except requests.RequestException as e:
            logger.error(f"Error initializing transaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Payment service error")

    @staticmethod
    async def verify_transaction(reference: str) -> dict:
        """
        Verify a Paystack transaction by reference.
        """
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(
                f"{PaystackService.BASE_URL}/transaction/verify/{reference}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("status") or data["data"]["status"] != "success":
                logger.error(f"Transaction verification failed for reference {reference}: {data.get('message')}")
                raise HTTPException(status_code=400, detail="Transaction verification failed")
            logger.info(f"Transaction verified for reference {reference}")
            return data["data"]
        except requests.RequestException as e:
            logger.error(f"Error verifying transaction: {str(e)}")
            raise HTTPException(status_code=500, detail="Payment verification error")