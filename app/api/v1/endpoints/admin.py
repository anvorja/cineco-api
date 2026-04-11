# app/api/v1/endpoints/admin.py - CORREGIDO CON IMPORTS
import hashlib
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.core.database import get_db
from app.api.dependencies import get_current_admin
from app.services.movie_service import MovieService
from app.services.purchase_service import PurchaseService
from app.schemas.movie import (
    MovieCreate, MovieUpdate, MovieResponse,
    CreateShowtimesRequest, TheaterResponse, TheaterCreate,
    ShowtimeResponse
)
from app.schemas.auth import UserResponse
from app.schemas.purchase import PurchaseResponse
from app.models import User
from app.models.theater import Theater
from app.schemas.blacklist import (
    BlacklistStats, BlacklistCleanupResponse, ForceLogoutResponse,
    BlacklistListResponse, TokenBlacklistResponse
)

router = APIRouter()


# ── Cloudinary signed upload ───────────────────────────────────────────────────

class CloudinarySignRequest(BaseModel):
    public_id: str
    folder: str = "cinema/movies"


@router.post("/cloudinary/sign")
async def sign_cloudinary_upload(
    body: CloudinarySignRequest,
    current_admin: User = Depends(get_current_admin)
):
    """Genera firma para upload directo a Cloudinary (preset Signed)."""
    if not settings.CLOUDINARY_API_SECRET:
        raise HTTPException(status_code=500, detail="Cloudinary no configurado en el servidor")

    timestamp = int(time.time())
    params = {
        "folder": body.folder,
        "public_id": body.public_id,
        "timestamp": str(timestamp),
        "upload_preset": settings.CLOUDINARY_UPLOAD_PRESET,
    }
    # Cloudinary: ordenar alfabéticamente y concatenar
    params_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    to_sign = params_string + settings.CLOUDINARY_API_SECRET
    signature = hashlib.sha1(to_sign.encode()).hexdigest()

    return {
        "signature": signature,
        "timestamp": timestamp,
        "api_key": settings.CLOUDINARY_API_KEY,
        "upload_preset": settings.CLOUDINARY_UPLOAD_PRESET,
    }


@router.post("/movies", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Crear nueva película (solo admin)"""
    movie = MovieService.create_movie(db=db, movie_data=movie_data)
    return MovieResponse.from_orm(movie)


@router.get("/movies", response_model=List[MovieResponse])
async def get_all_movies_admin(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    include_inactive: bool = Query(default=False, description="Incluir películas inactivas"),
    search: Optional[str] = Query(None, description="Buscar en título y descripción"),
    genre: Optional[str] = Query(None, description="Filtrar por género"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener todas las películas incluyendo inactivas"""
    movies = MovieService.get_movies(
        db=db,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
        search=search,
        genre=genre,
        available_only=False  # Admin puede ver todas
    )
    return [MovieResponse.from_orm(movie) for movie in movies]


@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie_admin(
    movie_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener detalles de película incluyendo inactivas"""
    movie = MovieService.get_movie_by_id(db=db, movie_id=movie_id, include_inactive=True)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Película no encontrada")
    return MovieResponse.from_orm(movie)


@router.put("/movies/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Actualizar información de película"""
    movie = MovieService.update_movie(db=db, movie_id=movie_id, movie_data=movie_data)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Película no encontrada")
    return MovieResponse.from_orm(movie)


@router.patch("/movies/{movie_id}/toggle", response_model=MovieResponse)
async def toggle_movie_status(
    movie_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Alternar estado activo/inactivo de película"""
    movie = MovieService.toggle_movie_status(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Película no encontrada")
    return MovieResponse.from_orm(movie)

# ======================
# 🏢 Theater Management
# ======================
@router.post("/theaters", response_model=TheaterResponse, status_code=status.HTTP_201_CREATED)
async def create_theater(
    theater_data: TheaterCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Crear nuevo teatro"""
    # Verificar que no existe
    existing = db.query(Theater).filter(Theater.name == theater_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Teatro '{theater_data.name}' ya existe"
        )

    theater = Theater(
        name=theater_data.name,
        location=theater_data.location,
        description=theater_data.description
    )

    db.add(theater)
    db.commit()
    db.refresh(theater)

    return TheaterResponse.from_orm(theater)


@router.get("/theaters", response_model=List[TheaterResponse])
async def get_all_theaters_admin(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener todos los teatros"""
    query = db.query(Theater)

    if not include_inactive:
        query = query.filter(Theater.is_active == True)

    theaters = query.offset(skip).limit(limit).all()
    return [TheaterResponse.from_orm(theater) for theater in theaters]


@router.post("/movies/{movie_id}/showtimes", response_model=List[ShowtimeResponse])
async def create_movie_showtimes(
    movie_id: int,
    showtimes_request: CreateShowtimesRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Crear horarios para una película específica"""
    created_showtimes = MovieService.create_showtimes_for_movie(
        db=db,
        movie_id=movie_id,
        start_date=showtimes_request.start_date,
        days_count=showtimes_request.days_count,
        theater_ids=showtimes_request.theater_ids
    )

    return [ShowtimeResponse.from_orm(showtime) for showtime in created_showtimes]


# ======================
# 👤 User Management
# ======================
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    include_inactive: bool = Query(default=False, description="Incluir usuarios inactivos"),
    search: Optional[str] = Query(None, description="Buscar por email o nombre"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener todos los usuarios del sistema"""
    query = db.query(User)

    if not include_inactive:
        query = query.filter(User.is_active == True)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )

    users = query.offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener detalles de usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return UserResponse.from_orm(user)


@router.patch("/users/{user_id}/toggle", response_model=UserResponse)
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Alternar estado activo/inactivo de usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    # Prevenir que admin se deshabilite a sí mismo
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes deshabilitar tu propia cuenta"
        )

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


# ======================
# 🛒 Purchase Management
# ======================
@router.get("/purchases", response_model=List[PurchaseResponse])
async def get_all_purchases(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    movie_id: Optional[int] = Query(None, description="Filtrar por ID de película"),
    user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener todas las compras del sistema"""
    purchases = PurchaseService.get_all_purchases(
        db=db,
        skip=skip,
        limit=limit,
        movie_id=movie_id,
        user_id=user_id,
        status=status
    )
    return [PurchaseResponse.from_orm(purchase) for purchase in purchases]


@router.get("/purchases/movie/{movie_id}", response_model=List[PurchaseResponse])
async def get_purchases_by_movie(
    movie_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener todas las compras para una película específica"""
    purchases = PurchaseService.get_all_purchases(
        db=db,
        skip=skip,
        limit=limit,
        movie_id=movie_id
    )
    return [PurchaseResponse.from_orm(purchase) for purchase in purchases]


@router.get("/purchases/user/{user_id}", response_model=List[PurchaseResponse])
async def get_purchases_by_user(
    user_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener todas las compras para un usuario específico"""
    purchases = PurchaseService.get_all_purchases(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id
    )
    return [PurchaseResponse.from_orm(purchase) for purchase in purchases]


@router.get("/reports/sales")
async def get_sales_report(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Obtener reporte consolidado de ventas"""
    return PurchaseService.get_sales_report(db=db)


# AGREGAR AL FINAL de app/api/v1/endpoints/admin.py

# ======================
# 🔒 Token Blacklist Management
# ======================
@router.get("/blacklist/stats", response_model=BlacklistStats)
async def get_blacklist_statistics(
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Obtener estadísticas completas de la blacklist de tokens.

    Incluye:
    - Total de tokens invalidados
    - Tokens invalidados en las últimas 24 horas
    - Distribución por razones de invalidación
    - Timestamp de generación del reporte
    """
    from app.services.token_service import TokenService

    stats = TokenService.get_blacklist_stats(db=db)
    return BlacklistStats(**stats)


@router.get("/blacklist/list", response_model=BlacklistListResponse)
async def list_blacklisted_tokens(
        page: int = Query(default=1, ge=1, description="Número de página"),
        page_size: int = Query(default=20, ge=1, le=100, description="Tamaño de página"),
        user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
        reason: Optional[str] = Query(None, description="Filtrar por razón"),
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Listar tokens en blacklist con paginación y filtros.

    Permite filtrar por usuario específico o razón de invalidación.
    """
    from app.models.token_blacklist import TokenBlacklist
    from sqlalchemy import desc

    # Query base
    query = db.query(TokenBlacklist)

    # Aplicar filtros
    if user_id:
        query = query.filter(TokenBlacklist.user_id == user_id)
    if reason:
        query = query.filter(TokenBlacklist.reason == reason)

    # Contar total
    total_count = query.count()

    # Calcular paginación
    offset = (page - 1) * page_size
    total_pages = (total_count + page_size - 1) // page_size

    # Obtener registros paginados
    tokens = query.order_by(desc(TokenBlacklist.blacklisted_at)).offset(offset).limit(page_size).all()

    return BlacklistListResponse(
        tokens=[TokenBlacklistResponse.from_orm(token) for token in tokens],
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/blacklist/cleanup", response_model=BlacklistCleanupResponse)
async def cleanup_blacklist(
        days_old: int = Query(default=30, ge=1, le=365, description="Limpiar tokens más viejos que X días"),
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Limpiar tokens expirados de la blacklist.

    Elimina tokens blacklisted más antiguos que el umbral especificado.
    Útil para mantener el tamaño de la blacklist bajo control.
    """
    from app.services.token_service import TokenService
    from datetime import datetime

    deleted_count = TokenService.cleanup_expired_tokens(db=db, days_old=days_old)

    return BlacklistCleanupResponse(
        message="Limpieza completada exitosamente",
        tokens_cleaned=deleted_count,
        days_threshold=days_old,
        cleanup_date=datetime.now().isoformat()
    )


@router.post("/users/{user_id}/logout-force", response_model=ForceLogoutResponse)
async def force_logout_user(
        user_id: int,
        reason: str = Query(default="admin_action", description="Razón del logout forzado"),
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Forzar logout de todas las sesiones de un usuario específico.

    Invalida inmediatamente todos los tokens activos del usuario.
    Útil para casos de emergencia de seguridad o suspensión de cuenta.
    """
    from app.services.token_service import TokenService

    # Verificar que el usuario existe
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Prevenir que admin se haga logout a sí mismo
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes forzar tu propio logout"
        )

    count = TokenService.blacklist_all_user_tokens(
        db=db,
        user_id=user_id,
        reason=f"admin_force_logout: {reason}"
    )

    return ForceLogoutResponse(
        message=f"Logout forzado aplicado al usuario {target_user.full_name}",
        user_id=user_id,
        sessions_closed=count,
        reason=reason,
        admin_user=current_admin.full_name
    )


@router.delete("/blacklist/{token_id}")
async def remove_token_from_blacklist(
        token_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Remover un token específico de la blacklist.

    ADVERTENCIA: Esto efectivamente "rehabilita" un token previamente invalidado.
    Solo usar en casos excepcionales o de debugging.
    """
    from app.models.token_blacklist import TokenBlacklist

    token_record = db.query(TokenBlacklist).filter(TokenBlacklist.id == token_id).first()
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token no encontrado en blacklist"
        )

    user_email = token_record.user_email
    db.delete(token_record)
    db.commit()

    return {
        "message": f"Token removido de blacklist para usuario {user_email}",
        "token_id": token_id,
        "admin_user": current_admin.full_name,
        "warning": "El token podría volver a ser válido si no ha expirado naturalmente"
    }
