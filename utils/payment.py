from dotenv import load_dotenv
import os
import requests
from repositories.ticket_repository import TicketRepository


load_dotenv()

def initialize_payment(user_email: str, purchase: dict) -> dict:
    ticket_type = TicketRepository.get_ticket_by_id(purchase.tickets[0].ticket_type_id)
    
    """
    Initialize the payment system.
    """
    return [{
        "status": "success",
        "message": "Payment initialized successfully",
        "payment_url": f"https://payment-gateway.com/pay"
    }]
    # payload = {
    #     "email": user_email,
    #     "amount": amount,
    # }

    # headers = {
    #     'Authorization': f"Bearer {os.getenv('SECRET_KEY')}",
    #     'Content-Type': 'application/json',
    # }

    # response = requests.post(os.getenv('API_URL'), json=payload, headers=headers)
    # return response.json()