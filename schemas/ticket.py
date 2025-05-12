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
    payment_status: Optional[str] = "pending"
    paystack_reference: Optional[str] = None
    qr_code: Optional[str] = None
    attendee_name: Optional[str] = None
    attendee_email: Optional[str] = None

class TicketVerification(BaseModel):
    valid: bool
    message: str