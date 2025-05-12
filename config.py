import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ticketing")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
    EMAIL_SERVICE_API_KEY: str = os.getenv("EMAIL_SERVICE_API_KEY", "")
    qrCode_PATH: str = os.getenv("qrCode_PATH", "/tmp/qrcodes")
    PAYSTACK_SECRET_KEY: str = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_your_paystack_secret_key")
    PAYSTACK_PUBLIC_KEY: str = os.getenv("PAYSTACK_PUBLIC_KEY", "pk_test_your_paystack_public_key")
    PAYSTACK_WEBHOOK_URL: str = os.getenv("PAYSTACK_WEBHOOK_URL", "http://localhost:8000/webhooks/paystack")


settings = Settings()

