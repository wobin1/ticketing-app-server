# app/repositories/ticket_repository.py
from repositories.db import Database
from schemas.ticket import Ticket
import logging
from uuid import uuid4
from datetime import datetime

logger = logging.getLogger(__name__)

class TicketRepository:
    @staticmethod
    async def purchase_ticket(event_id: str, user_id: str, ticket_type_id: str, price: float, qr_code: str, attendee_email: str = None, attendee_name: str = None) -> Ticket:
        ticket_id = f"tck_{uuid4()}"
        purchase_date = datetime.utcnow()
        try:
            with Database.get_connection() as conn:
                with conn.cursor() as cur:
                    # Check ticket type availability
                    cur.execute("""
                        SELECT available 
                        FROM ticket_types 
                        WHERE id = %s AND event_id = %s
                    """, (ticket_type_id, event_id))
                    result = cur.fetchone()
                    if not result or result[0] <= 0:
                        raise ValueError("No available tickets for this ticket type")
                    
                    # Insert ticket
                    cur.execute("""
                        INSERT INTO tickets (
                            id, event_id, user_id, ticket_type_id, 
                            purchase_date, status, payment_status, qr_code,
                            attendee_email, attendee_name
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """, (
                        ticket_id, event_id, user_id, ticket_type_id,
                        purchase_date, "pending", "pending", qr_code, attendee_email, attendee_name
                    ))
                    ticket_data = cur.fetchone()
                    
                    # Update ticket type availability
                    cur.execute("""
                        UPDATE ticket_types 
                        SET available = available - 1 
                        WHERE id = %s
                    """, (ticket_type_id,))
                    
                    conn.commit()
                    
                    return Ticket(
                        id=ticket_data[0],
                        event_id=ticket_data[1],
                        user_id=ticket_data[2],
                        ticket_type_id=ticket_data[3],
                        purchase_date=ticket_data[4],
                        status=ticket_data[5],
                        payment_status=ticket_data[7],
                        qr_code=ticket_data[8],
                        attendee_name=ticket_data[9],
                        attendee_email=ticket_data[10]
                    )
        except Exception as e:
            logger.error(f"Error purchasing ticket: {str(e)}")
            raise

    @staticmethod
    async def update_ticket_payment_reference(ticket_id: str, paystack_reference: str):
        try:
            with Database.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE tickets 
                        SET paystack_reference = %s 
                        WHERE id = %s
                    """, (paystack_reference, ticket_id))
                    conn.commit()
                    logger.info(f"Updated ticket {ticket_id} with Paystack reference {paystack_reference}")
        except Exception as e:
            logger.error(f"Error updating ticket reference: {str(e)}")
            raise

    @staticmethod
    async def update_ticket_payment_status(paystack_reference: str, payment_status: str):
        try:
            with Database.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE tickets 
                        SET payment_status = %s, status = %s 
                        WHERE paystack_reference = %s
                    """, (payment_status, "confirmed" if payment_status == "completed" else "pending", paystack_reference))
                    conn.commit()
                    logger.info(f"Updated ticket payment status for reference {paystack_reference} to {payment_status}")
        except Exception as e:
            logger.error(f"Error updating ticket payment status: {str(e)}")
            raise

    @staticmethod
    async def get_user_tickets(user_id: str) -> list[Ticket]:
        try:
            with Database.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, event_id, user_id, ticket_type_id, 
                            purchase_date, status, payment_status, qr_code, 
                            attendee_name, attendee_email
                        FROM tickets 
                        WHERE user_id = %s AND payment_status = 'completed'
                    """, (user_id,))
                    tickets = cur.fetchall()
                    return [
                        Ticket(
                            id=t[0], event_id=t[1], user_id=t[2], ticket_type_id=t[3],
                            purchase_date=t[4], status=t[5], payment_status=t[6],
                            qr_code=t[7], attendee_name=t[8], attendee_email=t[9]
                        ) for t in tickets
                    ]
        except Exception as e:
            logger.error(f"Error fetching user tickets: {str(e)}")
            raise   


    @staticmethod
    async def get_ticket_type_by_id(ticket_type_id: str):
        try:
            with Database.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, event_id, name, description, price, available
                        FROM ticket_types
                        WHERE id = %s
                    """, (ticket_type_id,))
                    ticket_type = cur.fetchone()
                    if ticket_type:
                        return {
                            'id': ticket_type[0],
                            'event_id': ticket_type[1],
                            'name': ticket_type[2],
                            'description': ticket_type[3],
                            'price': ticket_type[4],
                            'available': ticket_type[5]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error fetching ticket type: {str(e)}")
            raise


    @staticmethod
    async def get_all_tickets() -> list[Ticket]:
            try:
                with Database.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT id, event_id, user_id, ticket_type_id, 
                                purchase_date, status, payment_status, qr_code, 
                                attendee_name, attendee_email
                            FROM tickets
                        """)
                        tickets = cur.fetchall()
                        return [
                            Ticket(
                                id=t[0], event_id=t[1], user_id=t[2], ticket_type_id=t[3],
                                purchase_date=t[4], status=t[5], payment_status=t[6],
                                qr_code=t[7], attendee_name=t[8], attendee_email=t[9]
                            ) for t in tickets
                        ]
            except Exception as e:
                logger.error(f"Error fetching all tickets: {str(e)}")
                raise