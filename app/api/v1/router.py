# app/api/v1/router.py
from fastapi import APIRouter
from .endpoints import auth, movies, admin, purchases

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

# Include movies router (public endpoints)
api_router.include_router(
    movies.router,
    prefix="/movies",
    tags=["🎬 Movies"]
)

# Include purchases router (protected endpoints)
api_router.include_router(
    purchases.router,
    prefix="/purchases",
    tags=["🎫 Purchases"],
    responses={
        401: {"description": "Authentication required"}
    }
)


# Include admin router (protected endpoints)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["👨‍💼 Administration"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Admin privileges required"}
    }
)
