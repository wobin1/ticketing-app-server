# app/utils/seed.py
import logging
from repositories.db import Database
from utils.security import hash_password
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_database():
    """
    Seeds the database with initial data if key tables are empty.
    Includes users, events, ticket types, and tickets.
    """
    logger.info("Starting database seeding process")
    
    try:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                # Check if any key tables are empty
                cur.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM users) as user_count,
                        (SELECT COUNT(*) FROM events) as event_count,
                        (SELECT COUNT(*) FROM tickets) as ticket_count
                """)
                user_count, event_count, ticket_count = cur.fetchone()
                logger.info(f"Database state: users={user_count}, events={event_count}, tickets={ticket_count}")

                if user_count > 0 and event_count > 0 and ticket_count > 0:
                    logger.info("Database already contains data, skipping seeding")
                    return

                logger.info("Seeding database with initial data")

                # Seed Users
                users = [
                    {
                        "id": str(uuid.uuid4()),
                        "email": "admin@example.com",
                        "first_name": "Admin",
                        "last_name": "User",
                        "password": hash_password("adminpassword"),
                        "is_guest": False,
                        "role": "admin"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "email": "user@example.com",
                        "first_name": "Regular",
                        "last_name": "User",
                        "password": hash_password("userpassword"),
                        "is_guest": False,
                        "role": "user"
                    }
                ]
                for user in users:
                    cur.execute("""
                        INSERT INTO users (id, email, first_name, last_name, password, is_guest, role)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (email) DO NOTHING
                    """, (
                        user["id"],
                        user["email"],
                        user["first_name"],
                        user["last_name"],
                        user["password"],
                        user["is_guest"],
                        user["role"]
                    ))
                    logger.info(f"Seeded user: {user['email']}")

                # Seed Events and Ticket Types
                events = [
                    {
                        "id": "evt_001",
                        "name": "Summer Music Festival",
                        "description": "Join us for a day of live music featuring top artists across genres.",
                        "date": datetime(2025, 7, 12, 12, 0, 0),
                        "time": "12:00 PM",
                        "location": "Central Park, New York, NY",
                        "image_url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800&auto=format&fit=crop",
                        "ticket_types": [
                            {
                                "id": "tt_001_1",
                                "name": "General Admission",
                                "description": "Access to all festival areas except VIP zones.",
                                "price": 75.00,
                                "available": 500
                            },
                            {
                                "id": "tt_001_2",
                                "name": "VIP Pass",
                                "description": "Includes exclusive lounge access and premium viewing areas.",
                                "price": 150.00,
                                "available": 100
                            }
                        ]
                    },
                    {
                        "id": "evt_002",
                        "name": "Tech Conference 2025",
                        "description": "Explore the latest in AI, cloud computing, and cybersecurity.",
                        "date": datetime(2025, 9, 15, 9, 0, 0),
                        "time": "9:00 AM",
                        "location": "Moscone Center, San Francisco, CA",
                        "image_url": "https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=800&auto=format&fit=crop",
                        "ticket_types": [
                            {
                                "id": "tt_002_1",
                                "name": "Standard Ticket",
                                "description": "Access to all keynotes and breakout sessions.",
                                "price": 299.00,
                                "available": 1000
                            },
                            {
                                "id": "tt_002_2",
                                "name": "Premium Ticket",
                                "description": "Includes workshop access and priority seating.",
                                "price": 499.00,
                                "available": 200
                            }
                        ]
                    },
                    {
                        "id": "evt_003",
                        "name": "Comedy Night Live",
                        "description": "Laugh out loud with top comedians in an intimate venue.",
                        "date": datetime(2025, 6, 20, 20, 0, 0),
                        "time": "8:00 PM",
                        "location": "The Laugh Factory, Chicago, IL",
                        "image_url": "https://images.unsplash.com/photo-1485095329183-d0797cdc5676?w=800&auto=format&fit=crop",
                        "ticket_types": [
                            {
                                "id": "tt_003_1",
                                "name": "Standard Seat",
                                "description": "General seating in the main auditorium.",
                                "price": 35.00,
                                "available": 200
                            },
                            {
                                "id": "tt_003_2",
                                "name": "Front Row",
                                "description": "Prime front-row seating for the best experience.",
                                "price": 65.00,
                                "available": 20
                            }
                        ]
                    },
                    {
                        "id": "evt_004",
                        "name": "Art & Wine Festival",
                        "description": "Celebrate local artists and wineries with live music and tastings.",
                        "date": datetime(2025, 8, 3, 11, 0, 0),
                        "time": "11:00 AM",
                        "location": "Napa Valley, CA",
                        "image_url": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800&auto=format&fit=crop",
                        "ticket_types": [
                            {
                                "id": "tt_004_1",
                                "name": "General Entry",
                                "description": "Access to all festival areas and exhibitions.",
                                "price": 50.00,
                                "available": 300
                            },
                            {
                                "id": "tt_004_2",
                                "name": "Tasting Pass",
                                "description": "Includes wine tasting sessions with local vintners.",
                                "price": 85.00,
                                "available": 150
                            }
                        ]
                    },
                    {
                        "id": "evt_005",
                        "name": "Marathon 2025",
                        "description": "Run through the city in this annual marathon event.",
                        "date": datetime(2025, 10, 5, 7, 0, 0),
                        "time": "7:00 AM",
                        "location": "Boston, MA",
                        "image_url": "https://images.unsplash.com/photo-1513593771513-7b58b6c4af38?w=800&auto=format&fit=crop",
                        "ticket_types": [
                            {
                                "id": "tt_005_1",
                                "name": "5K Race",
                                "description": "Participate in the 5K fun run.",
                                "price": 30.00,
                                "available": 500
                            },
                            {
                                "id": "tt_005_2",
                                "name": "Half Marathon",
                                "description": "Run the half marathon course.",
                                "price": 75.00,
                                "available": 300
                            },
                            {
                                "id": "tt_005_3",
                                "name": "Full Marathon",
                                "description": "Challenge yourself with the full marathon.",
                                "price": 120.00,
                                "available": 200
                            }
                        ]
                    }
                ]
                for event in events:
                    cur.execute("""
                        INSERT INTO events (id, name, description, date, time, location, image_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (
                        event["id"],
                        event["name"],
                        event["description"],
                        event["date"],
                        event["time"],
                        event["location"],
                        event["image_url"]
                    ))
                    logger.info(f"Seeded event: {event['name']}")
                    for ticket_type in event["ticket_types"]:
                        cur.execute("""
                            INSERT INTO ticket_types (id, event_id, name, description, price, available)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                        """, (
                            ticket_type["id"],
                            event["id"],
                            ticket_type["name"],
                            ticket_type["description"],
                            ticket_type["price"],
                            ticket_type["available"]
                        ))
                        logger.info(f"Seeded ticket type: {ticket_type['name']} for event {event['name']}")

                # Seed Tickets
                tickets = [
                    {
                        "id": "tkt_001",
                        "event_id": "evt_001",
                        "user_id": users[1]["id"],  # Regular user
                        "ticket_type_id": "tt_001_1",
                        "purchase_date": datetime(2025, 5, 1, 10, 0, 0),
                        "status": "active",
                        "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==",
                        "attendee_name": "John Doe",
                        "attendee_email": "john.doe@example.com"
                    },
                    {
                        "id": "tkt_002",
                        "event_id": "evt_001",
                        "user_id": None,  # Guest purchase
                        "ticket_type_id": "tt_001_2",
                        "purchase_date": datetime(2025, 5, 2, 14, 30, 0),
                        "status": "active",
                        "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==",
                        "attendee_name": "Jane Smith",
                        "attendee_email": "jane.smith@example.com"
                    },
                    {
                        "id": "tkt_003",
                        "event_id": "evt_002",
                        "user_id": users[1]["id"],  # Regular user
                        "ticket_type_id": "tt_002_1",
                        "purchase_date": datetime(2025, 5, 3, 9, 15, 0),
                        "status": "used",
                        "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==",
                        "attendee_name": "Alice Johnson",
                        "attendee_email": "alice.johnson@example.com"
                    },
                    {
                        "id": "tkt_004",
                        "event_id": "evt_003",
                        "user_id": users[1]["id"],  # Regular user
                        "ticket_type_id": "tt_003_2",
                        "purchase_date": datetime(2025, 5, 4, 16, 45, 0),
                        "status": "active",
                        "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==",
                        "attendee_name": "Bob Wilson",
                        "attendee_email": "bob.wilson@example.com"
                    },
                    {
                        "id": "tkt_005",
                        "event_id": "evt_005",
                        "user_id": None,  # Guest purchase
                        "ticket_type_id": "tt_005_3",
                        "purchase_date": datetime(2025, 5, 5, 8, 20, 0),
                        "status": "canceled",
                        "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==",
                        "attendee_name": "Emma Brown",
                        "attendee_email": "emma.brown@example.com"
                    }
                ]
                for ticket in tickets:
                    cur.execute("""
                        INSERT INTO tickets (id, event_id, user_id, ticket_type_id, purchase_date, status, qr_code, attendee_name, attendee_email)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (
                        ticket["id"],
                        ticket["event_id"],
                        ticket["user_id"],
                        ticket["ticket_type_id"],
                        ticket["purchase_date"],
                        ticket["status"],
                        ticket["qrCode"],
                        ticket["attendee_name"],
                        ticket["attendee_email"]
                    ))
                    logger.info(f"Seeded ticket: {ticket['id']} for event {ticket['event_id']}")

                logger.info("Database seeding completed successfully")

    except Exception as e:
        logger.error(f"Error during seeding: {str(e)}")
        raise

