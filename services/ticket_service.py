from fastapi import HTTPException, status
from repositories.ticket_repository import TicketRepository
from repositories.event_repository import EventRepository
from repositories.user_repository import UserRepository
from schemas.ticket import Ticket, TicketPurchase, TicketVerification
from schemas.user import User, UserCreate
from services.qr_service import generate_qr_code
from services.email_service import send_ticket_email
from services.auth_service import create_user
import uuid
from datetime import datetime, timezone  # Update import
import logging

logger = logging.getLogger(__name__)

async def get_user_tickets(user_id: str) -> list[Ticket]:
    """
    Fetch all tickets for a user.
    """
    try:
        return await TicketRepository.get_user_tickets(user_id)
    except Exception as e:
        logger.error(f"Error fetching tickets for user {user_id}: {str(e)}")
        raise

async def getPrice(ticket_type_id: str) -> float:
    """
    Fetch the price of a ticket type.
    """
    try:
        ticket_type = await TicketRepository.get_ticket_type_by_id(ticket_type_id)
        print('ticket type data', ticket_type)
        if not ticket_type:
            raise HTTPException(status_code=404, detail="Ticket type not found")
        print('ticket price data', ticket_type)
        return ticket_type['price']
    except Exception as e:
        logger.error(f"Error fetching ticket type {ticket_type_id}: {str(e)}")
        raise

async def purchase_ticket(purchase: TicketPurchase, user_id: str) -> Ticket:
    """
    Purchase a ticke§t for an event.
    """
    print('purchase data', purchase.tickets[0].attendees[0])
    ticket_id = str(uuid.uuid4())
    qr_code = await generate_qr_code(ticket_id)
    ticket_price = await getPrice(purchase.tickets[0].ticket_type_id)  # Fetch price earlier
    try:
        ticket = await TicketRepository.purchase_ticket(
            event_id=purchase.event_id,
            user_id=user_id,
            ticket_type_id=purchase.tickets[0].ticket_type_id ,
            price=ticket_price,
            attendee_name=purchase.tickets[0].attendees[0].name,
            attendee_email=purchase.tickets[0].attendees[0].email,
            qr_code=qr_code,
        )
        logger.info(f"Ticket purchased: {ticket.id} for user {user_id}")
        return ticket
    except Exception as e:
        logger.error(f"Error purchasing ticket: {str(e)}")
        raise

async def verify_ticket(ticket_id: str) -> TicketVerification:
    ticket = await TicketRepository.get_ticket_by_id(ticket_id)
    if not ticket:
        return TicketVerification(valid=False, message="Ticket not found")
    if ticket["status"] == "used":
        return TicketVerification(valid=False, message="Ticket already checked in")
    if ticket["status"] == "canceled":
        return TicketVerification(valid=False, message="Ticket canceled")
    return TicketVerification(valid=True, message="Ticket valid")

async def check_in_ticket(ticket_id: str) -> Ticket | None:
    ticket = await TicketRepository.get_ticket_by_id(ticket_id)
    if not ticket:
        return None
    if ticket["status"] != "active":
        raise HTTPException(status_code=400, detail="Ticket cannot be checked in")
    
    await TicketRepository.update_ticket_status(ticket_id, "used")
    updated_ticket = await TicketRepository.get_ticket_by_id(ticket_id)
    return Ticket(**updated_ticket)

async def get_all_tickets() -> list[Ticket]:
    tickets = await TicketRepository.get_all_tickets()
    return tickets if isinstance(tickets[0], Ticket) else [Ticket(**ticket) for ticket in tickets]

async def cancel_ticket(ticket_id: str) -> Ticket | None:
    ticket = await TicketRepository.get_ticket_by_id(ticket_id)
    if not ticket:
        return None
    if ticket["status"] != "active":
        raise HTTPException(status_code=400, detail="Ticket cannot be canceled")
    
    await TicketRepository.update_ticket_status(ticket_id, "canceled")
    updated_ticket = await TicketRepository.get_ticket_by_id(ticket_id)
    return Ticket(**updated_ticket)
