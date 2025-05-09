from fastapi import HTTPException, status
from repositories.ticket_repository import TicketRepository
from repositories.event_repository import EventRepository
from repositories.user_repository import UserRepository
from schemas.ticket import Ticket, TicketPurchase, TicketVerification
from schemas.user import User, UserCreate
from services.qr_service import generate_qrCode
from services.email_service import send_ticket_email
from services.auth_service import create_user
import uuid
from datetime import datetime, timezone  # Update import

async def get_user_tickets(user_id: str) -> list[Ticket]:
    tickets = await TicketRepository.get_tickets_by_user(user_id)
    return [Ticket(**ticket) for ticket in tickets]

async def purchase_tickets(purchase: TicketPurchase, current_user: User) -> list[Ticket]:
    event = await EventRepository.get_event_by_id(purchase.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    tickets = []
    for item in purchase.tickets:
        ticket_type = next((tt for tt in event["ticket_types"] if tt["id"] == item.ticket_type_id), None)
        if not ticket_type:
            raise HTTPException(status_code=400, detail=f"Invalid ticket type: {item.ticket_type_id}")
        if ticket_type["available"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough tickets available for {ticket_type['name']}")
        
        for attendee in item.attendees:
            ticket_id = str(uuid.uuid4())
            qrCode = await generate_qrCode(ticket_id)
            
            ticket = {
                "id": ticket_id,
                "event_id": purchase.event_id,
                "user_id": current_user.id,
                "ticket_type_id": item.ticket_type_id,
                "purchase_date": datetime.now(timezone.utc),
                "status": "active",
                "qrCode": qrCode,
                "attendee_name": attendee.name,
                "attendee_email": attendee.email
            }
            
            await TicketRepository.create_ticket(ticket)
            tickets.append(ticket)
            await send_ticket_email(attendee.email, ticket)
    
    # Update ticket availability
    for item in purchase.tickets:
        await EventRepository.update_ticket_type_availability(
            purchase.event_id,
            item.ticket_type_id,
            item.quantity
        )
    
    return [Ticket(**ticket) for ticket in tickets]

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
    return [Ticket(**ticket) for ticket in tickets]

async def cancel_ticket(ticket_id: str) -> Ticket | None:
    ticket = await TicketRepository.get_ticket_by_id(ticket_id)
    if not ticket:
        return None
    if ticket["status"] != "active":
        raise HTTPException(status_code=400, detail="Ticket cannot be canceled")
    
    await TicketRepository.update_ticket_status(ticket_id, "canceled")
    updated_ticket = await TicketRepository.get_ticket_by_id(ticket_id)
    return Ticket(**updated_ticket)
