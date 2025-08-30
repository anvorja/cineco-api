# app/api/v1/router.py
from fastapi import APIRouter
from .endpoints import auth

# Create main API router
api_router = APIRouter(
    prefix="/api/v1",
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation Error"}
    }
)

# Include authentication router
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["🔐 Authentication"],
    responses={401: {"description": "Authentication failed"}}
)