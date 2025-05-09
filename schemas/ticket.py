from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class TicketAttendee(BaseModel):
    name: str
    email: EmailStr

class TicketPurchaseItem(BaseModel):
    ticket_type_id: str
    quantity: int
    attendees: List[TicketAttendee]

class TicketPurchase(BaseModel):
    event_id: str
    tickets: List[TicketPurchaseItem]

class Ticket(BaseModel):
    id: str
    event_id: str
    user_id: Optional[str]
    ticket_type_id: str
    purchase_date: datetime
    status: str
    qr_code: str
    attendee_name: str
    attendee_email: EmailStr

class TicketVerification(BaseModel):
    valid: bool
    message: str