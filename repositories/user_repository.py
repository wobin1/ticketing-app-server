from repositories.db import Database
import uuid

class UserRepository:
    @staticmethod
    async def get_user_by_email(email: str) -> dict | None:
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, email, first_name, last_name, password, is_guest, role
                    FROM users
                    WHERE email = %s
                """, (email,))
                user = cur.fetchone()
                if user:
                    return {
                        "id": user[0],
                        "email": user[1],
                        "first_name": user[2],
                        "last_name": user[3],
                        "password": user[4],
                        "is_guest": user[5],
                        "role": user[6]
                    }
                return None

    @staticmethod
    async def create_user(user: dict) -> str:
        user_id = str(uuid.uuid4())
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (id, email, first_name, last_name, password, is_guest, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_id,
                    user["email"],
                    user["first_name"],
                    user["last_name"],
                    user["password"],
                    user["is_guest"],
                    user["role"]
                ))
                return cur.fetchone()[0]