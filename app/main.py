# app/main.py
import time
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, create_tables
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    logger.info("Starting Cinema Ticket API...")

    try:
        # Create tables if they don't exist
        create_tables()
        logger.info("Database tables created successfully")

        # Verify database connection
        with Session(engine) as session:
            session.execute(text("SELECT 1"))
        logger.info("Database connection verified")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    logger.info("Cinema Ticket API started successfully!")
    yield

    # Shutdown
    logger.info("Shutting down Cinema Ticket API...")
    engine.dispose()
    logger.info("Database connection closed")

# Create FastAPI app
app = FastAPI(
    title="Cinema Ticket API",
    description="API REST para sistema de compra de entradas de cine",
    version=settings.VERSION,
    contact={
        "name": "Cinema API Support",
        "email": "support@cinema.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    # Log request
    logger.info(f"[{request_id}] {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"[{request_id}] Status: {response.status_code} | "
        f"Time: {process_time:.2f}s"
    )

    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(api_router)

# Health check endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Cinema Ticket API",
        "status": "Working!",
        "version": settings.VERSION
    }

@app.get("/health", tags=["💻 Health"])
async def health_check():
    """Verificación detallada de salud con prueba de conexión a la base de datos"""
    try:
        with Session(engine) as db_session:
            db_session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as err:
        logger.error(f"Database health check failed: {err}")
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": settings.VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "database": db_status
    }

@app.exception_handler(500)
async def internal_server_error_handler(_request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )