from repositories.db import Database
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EventRepository:
    @staticmethod
    async def get_all_events() -> list[dict]:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.name, e.description, e.date, e.time, e.location, e.image_url,
                           array_agg(json_build_object(
                               'id', tt.id,
                               'name', tt.name,
                               'description', tt.description,
                               'price', tt.price,
                               'available', tt.available
                           )) as ticket_types
                    FROM events e
                    LEFT JOIN ticket_types tt ON e.id = tt.event_id
                    GROUP BY e.id
                """)
                events = cur.fetchall()
                return [{
                    "id": e[0],
                    "name": e[1],
                    "description": e[2],
                    "date": e[3],
                    "time": e[4],
                    "location": e[5],
                    "image_url": e[6],
                    "ticket_types": [t for t in e[7] if t["id"]] if e[7] else []
                } for e in events]

    @staticmethod
    async def get_event_by_id(event_id: str) -> dict | None:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.name, e.description, e.date, e.time, e.location, e.image_url,
                           array_agg(json_build_object(
                               'id', tt.id,
                               'name', tt.name,
                               'description', tt.description,
                               'price', tt.price,
                               'available', tt.available
                           )) as ticket_types
                    FROM events e
                    LEFT JOIN ticket_types tt ON e.id = tt.event_id
                    WHERE e.id = %s
                    GROUP BY e.id
                """, (event_id,))
                event = cur.fetchone()
                if event:
                    return {
                        "id": event[0],
                        "name": event[1],
                        "description": event[2],
                        "date": event[3],
                        "time": event[4],
                        "location": event[5],
                        "image_url": event[6],
                        "ticket_types": [t for t in event[7] if t["id"]] if event[7] else []
                    }
                return None

    @staticmethod
    async def search_events(query: str) -> list[dict]:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                search_pattern = f"%{query}%"
                logger.info(f"Executing search query with pattern: {search_pattern}")
                cur.execute("""
                    SELECT e.id, e.name, e.description, e.date, e.time, e.location, e.image_url,
                           array_agg(json_build_object(
                               'id', tt.id,
                               'name', tt.name,
                               'description', tt.description,
                               'price', tt.price,
                               'available', tt.available
                           )) as ticket_types
                    FROM events e
                    LEFT JOIN ticket_types tt ON e.id = tt.event_id
                    WHERE e.name ILIKE %s OR e.location ILIKE %s
                    GROUP BY e.id
                """, (search_pattern, search_pattern))
                events = cur.fetchall()
                result = [{
                    "id": e[0],
                    "name": e[1],
                    "description": e[2],
                    "date": e[3],
                    "time": e[4],
                    "location": e[5],
                    "image_url": e[6],
                    "ticket_types": [t for t in e[7] if t["id"]] if e[7] else []
                } for e in events]
                logger.info(f"Search returned {len(result)} events")
                return result

    @staticmethod
    async def create_event(event: dict) -> str:
        event_id = str(uuid.uuid4())
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (id, name, description, date, time, location, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    event_id,
                    event["name"],
                    event["description"],
                    event["date"],
                    event["time"],
                    event["location"],
                    event["image_url"]
                ))
                
                for ticket_type in event["ticket_types"]:
                    ticket_type_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO ticket_types (id, event_id, name, description, price, available)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        ticket_type_id,  # Generate new UUID for each ticket type
                        event_id,
                        ticket_type.name,  # Access Pydantic model attributes directly
                        ticket_type.description,
                        ticket_type.price,
                        ticket_type.available
                    ))
        return event_id

    @staticmethod
    async def update_event(event_id: str, event: dict) -> bool:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE events
                    SET name = %s, description = %s, date = %s, time = %s, location = %s, image_url = %s
                    WHERE id = %s
                    RETURNING id
                """, (
                    event["name"],
                    event["description"],
                    event["date"],
                    event["time"],
                    event["location"],
                    event["image_url"],
                    event_id
                ))
                if not cur.fetchone():
                    return False
                
                cur.execute("DELETE FROM ticket_types WHERE event_id = %s", (event_id,))
                for ticket_type in event["ticket_types"]:
                    cur.execute("""
                        INSERT INTO ticket_types (id, event_id, name, description, price, available)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        ticket_type["id"],
                        event_id,
                        ticket_type["name"],
                        ticket_type["description"],
                        ticket_type["price"],
                        ticket_type["available"]
                    ))
                return True

    @staticmethod
    async def delete_event(event_id: str) -> bool:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ticket_types WHERE event_id = %s", (event_id,))
                cur.execute("DELETE FROM tickets WHERE event_id = %s", (event_id,))
                cur.execute("DELETE FROM events WHERE id = %s RETURNING id", (event_id,))
                return bool(cur.fetchone())

    @staticmethod
    async def update_ticket_type_availability(event_id: str, ticket_type_id: str, quantity: int):
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ticket_types
                    SET available = available - %s
                    WHERE id = %s AND event_id = %s
                """, (quantity, ticket_type_id, event_id))