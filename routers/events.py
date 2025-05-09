# app/routers/events.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.event import Event, EventCreate, EventUpdate
from services.event_service import get_events, get_event, search_events, create_event, update_event, delete_event
from dependencies import get_current_active_user, get_current_admin_user
from schemas.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/debug", response_model=dict)
async def debug_endpoint():
    logger.info("Debug endpoint reached")
    return {"message": "Events router is active"}

@router.get("/", response_model=List[Event])
async def list_events():
    logger.info("Listing all events")
    return await get_events()

@router.get("/search", response_model=List[Event])
async def search_events_by_query(query: str):
    logger.info(f"Searching events with query: '{query}'")
    try:
        events = await search_events(query.strip())
        logger.info(f"Found {len(events)} events for query: '{query}'")
        return events
    except Exception as e:
        logger.error(f"Error searching events: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{event_id}", response_model=Event)
async def get_event_by_id(event_id: str):
    logger.info(f"Fetching event with ID: {event_id}")
    event = await get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/", response_model=Event, dependencies=[Depends(get_current_admin_user)])
async def create_new_event(event: EventCreate):
    logger.info("Creating new event")
    return await create_event(event)

@router.put("/{event_id}", response_model=Event, dependencies=[Depends(get_current_admin_user)])
async def update_existing_event(event_id: str, event: EventUpdate):
    logger.info(f"Updating event with ID: {event_id}")
    updated_event = await update_event(event_id, event)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@router.delete("/{event_id}", status_code=204, dependencies=[Depends(get_current_admin_user)])
async def delete_existing_event(event_id: str):
    logger.info(f"Deleting event with ID: {event_id}")
    success = await delete_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")