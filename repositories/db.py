import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from config import settings

class Database:
    _pool = None

    @classmethod
    def initialize(cls):
        cls._pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            dsn=settings.DATABASE_URL
        )

    @classmethod
    @contextmanager
    def get_connection(cls):
        conn = cls._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cls._pool.putconn(conn)

Database.initialize()