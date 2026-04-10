# app/api/v1/endpoints/movies.py - CORREGIDO
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.movie_service import MovieService
from app.models.movie import MovieStatus, Movie
from app.models.theater import Theater
from app.schemas.movie import (
    MovieListResponse, MovieWithShowtimesResponse,
    ShowtimeResponse, TheaterResponse
)

router = APIRouter()


@router.get("", response_model=List[MovieListResponse])
async def get_movies(
        skip: int = Query(default=0, ge=0, description="Registros a omitir"),
        limit: int = Query(default=10, ge=1, le=50, description="Máximo registros a retornar"),
        # Filtros mejorados
        status: Optional[str] = Query(default=None, description="Estado: in_theaters, coming_soon, ended"),
        is_presale: Optional[bool] = Query(default=None, description="Solo películas en preventa"),
        theater: Optional[str] = Query(default=None, description="Filtrar por teatro"),
        db: Session = Depends(get_db)
):
    """
    Obtener películas disponibles con filtros mejorados.

    Por defecto muestra solo películas que se pueden ver:
    - En cartelera (in_theaters)
    - Próximos estrenos en preventa (coming_soon + is_presale=true)
    """
    # Si no especifica status, mostrar películas "disponibles"
    if status is None:
        available_movies = MovieService.get_movies(
            db=db,
            skip=skip,
            limit=limit,
            include_inactive=False,
            theater_name=theater,
            is_presale=is_presale,
            available_only=True
        )
    else:
        # Usar status específico
        try:
            movie_status = MovieStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Estado inválido")

        movies = MovieService.get_movies(
            db=db,
            skip=skip,
            limit=limit,
            include_inactive=False,
            status=movie_status,
            is_presale=is_presale,
            theater_name=theater,
            available_only=True
        )
        available_movies = movies

    return [MovieListResponse.from_orm(movie) for movie in available_movies]


@router.get("/search", response_model=List[MovieListResponse])
async def search_movies(
        q: Optional[str] = Query(None, description="Búsqueda en título, descripción y director"),
        genre: Optional[str] = Query(None, description="Filtrar por género"),
        director: Optional[str] = Query(None, description="Filtrar por director"),
        country: Optional[str] = Query(None, description="Filtrar por país"),
        min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
        max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),
        rating: Optional[str] = Query(None, pattern="^(G|PG|PG-13|R|NC-17)$", description="Clasificación"),
        status: Optional[str] = Query(None, description="Estado de la película"),
        theater: Optional[str] = Query(None, description="Filtrar por teatro"),
        available_only: bool = Query(True, description="Solo películas con tickets disponibles"),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=50),
        db: Session = Depends(get_db)
):
    """Búsqueda avanzada de películas con múltiples filtros."""
    movie_status = None
    if status:
        try:
            movie_status = MovieStatus(status)
        except ValueError:
            movie_status = None

    movies = MovieService.get_movies(
        db=db,
        skip=skip,
        limit=limit,
        search=q,
        genre=genre,
        director=director,
        country=country,
        min_price=min_price,
        max_price=max_price,
        rating=rating,
        status=movie_status,
        theater_name=theater,
        available_only=available_only
    )

    return [MovieListResponse.from_orm(movie) for movie in movies]


@router.get("/coming-soon", response_model=List[MovieListResponse])
async def get_coming_soon_movies(
        limit: int = Query(default=10, ge=1, le=20, description="Máximo películas a retornar"),
        db: Session = Depends(get_db)
):
    """Obtener próximos estrenos ordenados por fecha de estreno."""
    movies = MovieService.get_movies_coming_soon(db=db, limit=limit)
    return [MovieListResponse.from_orm(movie) for movie in movies]


@router.get("/presales", response_model=List[MovieListResponse])
async def get_presale_movies(
        limit: int = Query(default=10, ge=1, le=20, description="Máximo películas a retornar"),
        db: Session = Depends(get_db)
):
    """Obtener películas en preventa."""
    movies = MovieService.get_movies_in_presale(db=db, limit=limit)
    return [MovieListResponse.from_orm(movie) for movie in movies]


@router.get("/{movie_id}", response_model=MovieWithShowtimesResponse)
async def get_movie_with_showtimes(
        movie_id: int,
        db: Session = Depends(get_db)
):
    """Obtener información detallada de una película incluyendo horarios y teatros."""
    movie = MovieService.get_movie_with_showtimes(db=db, movie_id=movie_id, include_inactive=False)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Película no encontrada"
        )

    return MovieWithShowtimesResponse.from_orm(movie)


@router.get("/{movie_id}/showtimes", response_model=List[ShowtimeResponse])
async def get_movie_showtimes(
        movie_id: int,
        theater_id: Optional[int] = Query(None, description="Filtrar por teatro específico"),
        start_date: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
        db: Session = Depends(get_db)
):
    """Obtener horarios específicos de una película."""
    # Verificar que la película existe
    movie = MovieService.get_movie_by_id(db=db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    showtimes = MovieService.get_movie_showtimes(
        db=db,
        movie_id=movie_id,
        theater_id=theater_id,
        start_date=start_date,
        end_date=end_date
    )

    return [ShowtimeResponse.from_orm(showtime) for showtime in showtimes]


@router.get("/{movie_id}/theaters", response_model=List[TheaterResponse])
async def get_movie_theaters(
        movie_id: int,
        db: Session = Depends(get_db)
):
    """Obtener todos los teatros donde se proyecta una película."""
    theaters = MovieService.get_theaters_for_movie(db=db, movie_id=movie_id)
    if theaters is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return [TheaterResponse.from_orm(theater) for theater in theaters]


@router.get("/{movie_id}/availability", response_model=dict)
async def get_movie_availability(
        movie_id: int,
        db: Session = Depends(get_db)
):
    """Información completa de disponibilidad incluyendo teatros y horarios."""
    movie = MovieService.get_movie_with_showtimes(db=db, movie_id=movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    # Filtrar los próximos 3 días de los showtimes ya cargados (evita segunda query)
    today = date.today()
    cutoff = today + timedelta(days=3)
    upcoming_showtimes = [
        st for st in movie.showtimes
        if st.is_active and today <= st.show_date <= cutoff
    ]

    # Agrupar por fecha
    showtimes_by_date = {}
    for showtime in upcoming_showtimes:
        date_key = showtime.show_date.isoformat()
        if date_key not in showtimes_by_date:
            showtimes_by_date[date_key] = []

        showtimes_by_date[date_key].append({
            "theater": showtime.theater.name,
            "time": showtime.show_time,
            "format": showtime.format.value,
            "available_tickets": showtime.available_tickets,
            "capacity": showtime.capacity
        })

    # Información de disponibilidad de compra
    availability_info = movie.get_purchase_availability_info()

    return {
        "movie_id": movie.id,
        "title": movie.title,
        "director": movie.director,
        "status": movie.status.value,
        "is_presale": movie.is_presale,
        "release_date": movie.formatted_release_date,
        "price": movie.price,
        "theaters": movie.theaters,
        "total_capacity": movie.max_capacity,
        "total_available": movie.available_tickets,
        "is_available": movie.is_available,
        "occupancy_rate": movie.occupancy_rate,
        "upcoming_showtimes": showtimes_by_date,
        "purchase_availability": availability_info
    }
