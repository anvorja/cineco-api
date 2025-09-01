# app/api/v1/endpoints/theaters.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.movie import TheaterResponse, MovieListResponse
from app.models.theater import Theater, TheaterMovie
from app.models.movie import Movie, MovieStatus

router = APIRouter()


@router.get("/", response_model=List[TheaterResponse])
async def get_all_theaters(db: Session = Depends(get_db)):
    """
    Obtener lista de teatros disponibles (público).

    Retorna todos los teatros activos en el sistema.
    """
    theaters = db.query(Theater).filter(Theater.is_active == True).all()
    return [TheaterResponse.from_orm(theater) for theater in theaters]


@router.get("/{theater_id}", response_model=TheaterResponse)
async def get_theater_by_id(
        theater_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener información detallada de un teatro específico.
    """
    theater = db.query(Theater).filter(
        Theater.id == theater_id,
        Theater.is_active == True
    ).first()

    if not theater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teatro no encontrado"
        )

    return TheaterResponse.from_orm(theater)


@router.get("/{theater_id}/movies", response_model=List[MovieListResponse])
async def get_theater_movies(
        theater_id: int,
        status: Optional[str] = Query(default="in_theaters", description="Filtrar por estado de película"),
        skip: int = Query(default=0, ge=0, description="Registros a omitir"),
        limit: int = Query(default=20, ge=1, le=100, description="Máximo registros a retornar"),
        db: Session = Depends(get_db)
):
    """
    Obtener todas las películas que se proyectan en un teatro específico.

    - **theater_id**: ID del teatro
    - **status**: Estado de las películas (in_theaters, coming_soon, ended)
    - **skip**: Paginación - registros a omitir
    - **limit**: Paginación - máximo registros
    """
    # Verificar que el teatro existe
    theater = db.query(Theater).filter(
        Theater.id == theater_id,
        Theater.is_active == True
    ).first()

    if not theater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teatro no encontrado"
        )

    # Construir query base
    query = db.query(Movie).join(TheaterMovie).filter(
        TheaterMovie.theater_id == theater_id,
        TheaterMovie.is_active == True,
        Movie.is_active == True
    )

    # Aplicar filtro de status si se proporciona
    if status:
        try:
            movie_status = MovieStatus(status)
            query = query.filter(Movie.status == movie_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido: {status}. Valores válidos: in_theaters, coming_soon, ended"
            )

    # Aplicar paginación y ordenamiento
    movies = query.order_by(Movie.created_at.desc()).offset(skip).limit(limit).all()

    return [MovieListResponse.from_orm(movie) for movie in movies]


@router.get("/{theater_id}/schedule", response_model=dict)
async def get_theater_schedule(
        theater_id: int,
        date: Optional[str] = Query(None, description="Fecha específica (YYYY-MM-DD), por defecto hoy"),
        db: Session = Depends(get_db)
):
    """
    Obtener programación completa de un teatro para una fecha específica.

    Retorna todas las funciones del teatro organizadas por película y horario.
    """
    from datetime import date as date_type, datetime
    from app.models.theater import MovieShowtime
    from sqlalchemy.orm import joinedload

    # Verificar que el teatro existe
    theater = db.query(Theater).filter(
        Theater.id == theater_id,
        Theater.is_active == True
    ).first()

    if not theater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teatro no encontrado"
        )

    # Parsear fecha o usar hoy
    target_date = date_type.today()
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Use YYYY-MM-DD"
            )

    # Obtener horarios del teatro para la fecha
    showtimes = db.query(MovieShowtime).options(
        joinedload(MovieShowtime.movie)
    ).filter(
        MovieShowtime.theater_id == theater_id,
        MovieShowtime.show_date == target_date,
        MovieShowtime.is_active == True
    ).order_by(MovieShowtime.show_time).all()

    # Organizar por película
    movies_schedule = {}
    for showtime in showtimes:
        movie_id = showtime.movie_id
        movie_title = showtime.movie.title

        if movie_id not in movies_schedule:
            movies_schedule[movie_id] = {
                "movie": {
                    "id": movie_id,
                    "title": movie_title,
                    "director": showtime.movie.director,
                    "duration": showtime.movie.duration,
                    "rating": showtime.movie.rating,
                    "poster_url": showtime.movie.poster_url,
                    "price": showtime.movie.price
                },
                "showtimes": []
            }

        movies_schedule[movie_id]["showtimes"].append({
            "id": showtime.id,
            "time": showtime.show_time,
            "format": showtime.format.value,
            "available_tickets": showtime.available_tickets,
            "capacity": showtime.capacity,
            "occupancy_percent": round((1 - showtime.available_tickets / showtime.capacity) * 100, 1)
        })

    return {
        "theater": {
            "id": theater.id,
            "name": theater.name,
            "location": theater.location
        },
        "date": target_date.isoformat(),
        "formatted_date": target_date.strftime("%d-%b-%Y"),
        "movies": list(movies_schedule.values()),
        "total_showtimes": len(showtimes)
    }
