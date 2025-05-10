from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, events, tickets
from config import settings
from utils.seed import seed_database
from utils.db_init import create_tables
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Event Ticketing API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: Initializing database")
    try:
        await create_tables()  # Create tables first
        await seed_database()  # Then seed data
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

@app.get("/")
async def root():
    return {"message": "Event Ticketing API"}