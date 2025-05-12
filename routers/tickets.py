from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.ticket import Ticket, TicketPurchase, TicketVerification
from services.ticket_service import get_user_tickets, purchase_ticket, verify_ticket, get_all_tickets
from services.payment_service import PaystackService
from dependencies import get_current_active_user, get_current_admin_user
from repositories.ticket_repository import TicketRepository
from schemas.user import User
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/user", response_model=List[Ticket])
async def list_user_tickets(current_user: User = Depends(get_current_active_user)):
    logger.info(f"Fetching tickets for user: {current_user.email} with ID: {current_user.id}")
    tickets = await get_user_tickets(current_user.id)
    logger.info(f"Found {len(tickets)} tickets for user {current_user.email}")
    return tickets

@router.post("/purchase", response_model=dict)
async def purchase_ticket_endpoint(
    purchase: TicketPurchase,
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"Initiating ticket purchase for user: {current_user.email}, event: {purchase.event_id}")
    try:    
        # Purchase ticket and get ticket ID
        ticket = await purchase_ticket(purchase, current_user.id)
        purchase_amount = await TicketRepository.get_ticket_type_by_id(purchase.tickets[0].ticket_type_id)
        print('purchase amount', purchase_amount['price'])
        if not purchase_amount:
            raise HTTPException(status_code=404, detail="Ticket type not found")
        
        # Initialize Paystack transaction
        callback_url = f"{settings.CORS_ORIGINS[0]}/confirmation"
        payment_data = await PaystackService.initialize_transaction(
            email=current_user.email,
            amount=purchase_amount["price"],  # Paystack expects amount in kobo
            ticket_id=ticket.id,
            callback_url=callback_url
        )
        
        # Update ticket with Paystack reference
        await TicketRepository.update_ticket_payment_reference(ticket.id, payment_data["reference"])
        
        return {
            "authorization_url": payment_data["authorization_url"],
            "access_code": payment_data["access_code"],
            "reference": payment_data["reference"],
        }
    except Exception as e:
        logger.error(f"Error processing purchase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process purchase")

@router.post("/webhooks/paystack")
async def paystack_webhook(payload: dict):
    """
    Handle Paystack webhook events (e.g., charge.success).
    """
    logger.info(f"Received Paystack webhook: {payload.get('event')}")
    if payload.get("event") == "charge.success":
        try:
            reference = payload["data"]["reference"]
            # Verify transaction
            transaction = await PaystackService.verify_transaction(reference)
            
            # Update ticket payment status
            await TicketRepository.update_ticket_payment_status(reference, "completed")
            
            logger.info(f"Payment confirmed for reference {reference}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise HTTPException(status_code=500, detail="Webhook processing error")
    
    return {"status": "ignored"}


@router.get("/verify/{ticket_id}", response_model=TicketVerification)
async def verify_ticket_by_id(ticket_id: str):
    return await verify_ticket(ticket_id)

@router.post("/check-in/{ticket_id}", response_model=Ticket)
async def check_in_ticket_by_id(ticket_id: str):
    ticket = await check_in_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("/all", response_model=List[Ticket], dependencies=[Depends(get_current_admin_user)])
async def list_all_tickets():
    return await get_all_tickets()

@router.post("/cancel/{ticket_id}", response_model=Ticket, dependencies=[Depends(get_current_admin_user)])
async def cancel_ticket_by_id(ticket_id: str):
    ticket = await cancel_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket