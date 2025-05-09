from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.ticket import Ticket, TicketPurchase, TicketVerification
from services.ticket_service import get_user_tickets, purchase_tickets, verify_ticket, check_in_ticket, get_all_tickets, cancel_ticket
from dependencies import get_current_active_user, get_current_admin_user
from schemas.user import User

router = APIRouter()

@router.get("/user", response_model=List[Ticket])
async def list_user_tickets(current_user: User = Depends(get_current_active_user)):
    return await get_user_tickets(current_user.id)

@router.post("/purchase", response_model=List[Ticket])
async def purchase_new_tickets(purchase: TicketPurchase, current_user: User = Depends(get_current_active_user)):
    return await purchase_tickets(purchase, current_user)

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