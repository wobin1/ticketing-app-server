from repositories.db import Database
from datetime import datetime

class TicketRepository:
    @staticmethod
    async def get_tickets_by_user(user_id: str) -> list[dict]:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, event_id, user_id, ticket_type_id, purchase_date, status, qr_code, attendee_name, attendee_email
                    FROM tickets
                    WHERE user_id = %s
                """, (user_id,))
                tickets = cur.fetchall()
                return [{
                    "id": t[0],
                    "event_id": t[1],
                    "user_id": t[2],
                    "ticket_type_id": t[3],
                    "purchase_date": t[4],
                    "status": t[5],
                    "qr_code": t[6],
                    "attendee_name": t[7],
                    "attendee_email": t[8]
                } for t in tickets]

    @staticmethod
    async def get_ticket_by_id(ticket_id: str) -> dict | None:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, event_id, user_id, ticket_type_id, purchase_date, status, qr_code, attendee_name, attendee_email
                    FROM tickets
                    WHERE id = %s
                """, (ticket_id,))
                ticket = cur.fetchone()
                if ticket:
                    return {
                        "id": ticket[0],
                        "event_id": ticket[1],
                        "user_id": ticket[2],
                        "ticket_type_id": ticket[3],
                        "purchase_date": ticket[4],
                        "status": ticket[5],
                        "qr_code": ticket[6],
                        "attendee_name": ticket[7],
                        "attendee_email": ticket[8]
                    }
                return None

    @staticmethod
    async def create_ticket(ticket: dict):
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tickets (id, event_id, user_id, ticket_type_id, purchase_date, status, qr_code, attendee_name, attendee_email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ticket["id"],
                    ticket["event_id"],
                    ticket["user_id"],
                    ticket["ticket_type_id"],
                    ticket["purchase_date"],
                    ticket["status"],
                    ticket["qr_code"],
                    ticket["attendee_name"],
                    ticket["attendee_email"]
                ))

    @staticmethod
    async def update_ticket_status(ticket_id: str, status: str):
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE tickets
                    SET status = %s
                    WHERE id = %s
                """, (status, ticket_id))

    @staticmethod
    async def get_all_tickets() -> list[dict]:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, event_id, user_id, ticket_type_id, purchase_date, status, qr_code, attendee_name, attendee_email
                    FROM tickets
                """)
                tickets = cur.fetchall()
                return [{
                    "id": t[0],
                    "event_id": t[1],
                    "user_id": t[2],
                    "ticket_type_id": t[3],
                    "purchase_date": t[4],
                    "status": t[5],
                    "qr_code": t[6],
                    "attendee_name": t[7],
                    "attendee_email": t[8]
                } for t in tickets]
