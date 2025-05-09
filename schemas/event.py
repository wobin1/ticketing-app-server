from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TicketTypeBase(BaseModel):
    id: str
    name: str
    description: str
    price: float
    available: int

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketType(TicketTypeBase):
    pass

class EventBase(BaseModel):
    name: str
    description: str
    date: datetime
    time: str
    location: str
    image_url: str

class EventCreate(EventBase):
    ticket_types: List[TicketTypeCreate]

class EventUpdate(EventBase):
    ticket_types: List[TicketTypeCreate]

class Event(EventBase):
    id: str
    ticket_types: List[TicketType]