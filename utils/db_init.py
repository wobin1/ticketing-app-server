from repositories.db import Database
import logging

logger = logging.getLogger(__name__)

async def create_tables():
    """
    Creates database tables if they don't exist.
    """
    logger.info("Initializing database tables")
    
    create_tables_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(36) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        password VARCHAR(255) NOT NULL,
        is_guest BOOLEAN DEFAULT FALSE,
        role VARCHAR(20) DEFAULT 'user'
    );

    CREATE TABLE IF NOT EXISTS events (
        id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        date TIMESTAMP NOT NULL,
        time VARCHAR(50) NOT NULL,
        location VARCHAR(255) NOT NULL,
        image_url TEXT
    );

    CREATE TABLE IF NOT EXISTS ticket_types (
        id VARCHAR(50) PRIMARY KEY,
        event_id VARCHAR(50) REFERENCES events(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        available INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tickets (
        id VARCHAR(50) PRIMARY KEY,
        event_id VARCHAR(50) REFERENCES events(id) ON DELETE CASCADE,
        user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
        ticket_type_id VARCHAR(50) REFERENCES ticket_types(id) ON DELETE CASCADE,
        purchase_date TIMESTAMP NOT NULL,
        status VARCHAR(20) NOT NULL,
        qr_code TEXT,
        attendee_name VARCHAR(255),
        attendee_email VARCHAR(255)
    );
    """

    try:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                # Check if tables exist
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('users', 'events', 'ticket_types', 'tickets')
                """)
                existing_tables = cur.fetchone()[0]
                
                if existing_tables == 4:
                    logger.info("All tables already exist, skipping creation")
                    return

                # Execute table creation SQL
                cur.execute(create_tables_sql)
                conn.commit()
                logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise