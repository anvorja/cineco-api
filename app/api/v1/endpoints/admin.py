# app/api/v1/endpoints/admin.py - CORREGIDO CON IMPORTS
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

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

router = APIRouter()


# ======================
# 🎬 Movie Management
# ======================
@router.post("/movies", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Crear nueva película (admin only)"""
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
    """Obtener todas las películas incluyendo inactivas (admin only)"""
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
    """Obtener detalles de película incluyendo inactivas (admin only)"""
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
    """Actualizar información de película (admin only)"""
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
    """Alternar estado activo/inactivo de película (admin only)"""
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
    """Crear nuevo teatro (admin only)"""
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
    """Obtener todos los teatros (admin only)"""
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
    """Crear horarios para una película específica (admin only)"""
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
    """Obtener todos los usuarios del sistema (admin only)"""
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
    """Obtener detalles de usuario (admin only)"""
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
    """Alternar estado activo/inactivo de usuario (admin only)"""
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
    """Obtener todas las compras del sistema (admin only)"""
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
    """Obtener todas las compras para una película específica (admin only)"""
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
    """Obtener todas las compras para un usuario específico (admin only)"""
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
    """Obtener reporte consolidado de ventas (admin only)"""
    return PurchaseService.get_sales_report(db=db)
