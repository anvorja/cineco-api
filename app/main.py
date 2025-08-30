# app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import create_tables, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown lifecycle"""
    logger.info("🚀 Starting Cinema Ticket API...")

    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")

        # Create or verify tables
        create_tables()
        logger.info("✅ Database tables created/verified")

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise

    logger.info("🎬 Cinema Ticket API started successfully!")
    yield  # <-- Aquí la app queda corriendo

    # Shutdown
    logger.info("🛑 Shutting down Cinema Ticket API...")


# Create FastAPI app
app = FastAPI(
    title="🎬 Cinema Ticket API",
    description="API REST para sistema de compra de entradas de cine",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "🎬 Cinema Ticket API",
        "status": "Working!",
        "version": settings.VERSION,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "database": db_status,
        "environment": "development" if settings.DEBUG else "production",
    }
