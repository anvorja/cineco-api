# app/api/v1/router.py
from fastapi import APIRouter
from .endpoints import admin, users
# purchases  → migrado a booking-service  (Phase 3, Traefik /api/v1/purchases → :8004)
# auth       → migrado a auth-service     (Phase 4, Traefik /api/v1/auth     → :8005)
# movies     → migrado a catalog-service  (Phase 4, Traefik /api/v1/movies   → :8006)
# theaters   → migrado a catalog-service  (Phase 4, Traefik /api/v1/theaters → :8006)
# calendar   → migrado a catalog-service  (Phase 4, Traefik /api/v1/calendar → :8006)

# Create main API router — solo admin y users permanecen en el monolito
api_router = APIRouter(
    prefix="/api/v1",
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation Error"}
    }
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["👤 User"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["👨‍💼 Administration"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Admin privileges required"}
    }
)

