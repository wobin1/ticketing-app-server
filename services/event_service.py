from fastapi import HTTPException
from repositories.event_repository import EventRepository
from schemas.event import Event, EventCreate, EventUpdate, TicketType
import logging

logger = logging.getLogger(__name__)

async def get_events() -> list[Event]:
    events = await EventRepository.get_all_events()
    return [Event(**event) for event in events]  # Remove explicit ticket_types argument

async def get_event(event_id: str) -> Event | None:
    event = await EventRepository.get_event_by_id(event_id)
    if not event:
        return None
    return Event(**event)

async def search_events(query: str) -> list[Event]:
    sanitized_query = query.strip()
    logger.info(f"Sanitized search query: '{sanitized_query}'")
    events = await EventRepository.search_events(sanitized_query)
    return [Event(**event) for event in events]

async def create_event(event: EventCreate) -> Event:
    event_id = await EventRepository.create_event({
        **event.dict(exclude={"ticket_types"}),
        "ticket_types": event.ticket_types
    })
    created_event = await EventRepository.get_event_by_id(event_id)
    return Event(**created_event)

async def update_event(event_id: str, event: EventUpdate) -> Event | None:
    success = await EventRepository.update_event(event_id, {
        **event.dict(exclude={"ticket_types"}),
        "ticket_types": event.ticket_types
    })
    if not success:
        return None
    updated_event = await EventRepository.get_event_by_id(event_id)
    return Event(**updated_event, ticket_types=updated_event["ticket_types"])

async def delete_event(event_id: str) -> bool:
    return await EventRepository.delete_event(event_id)