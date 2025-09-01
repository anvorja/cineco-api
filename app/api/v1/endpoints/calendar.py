# app/api/v1/endpoints/calendar.py
from typing import Optional, Dict, Any
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.theater import Theater, MovieShowtime, ShowtimeFormat  # ← AGREGAR ShowtimeFormat
from app.models import Movie

router = APIRouter()

@router.get("/calendar/week", response_model=Dict[str, Any])
async def get_week_calendar(
        start_date: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD). Por defecto: hoy"),
        db: Session = Depends(get_db)
):
    """
    Obtener calendario semanal como en las imágenes de referencia.

    Retorna la programación de 7 días con el formato:
    - Fechas en formato SEP 3, 4, 5, 6, 7
    - Funciones por multiplex/teatro
    - Horarios agrupados por formato (2D Doblado, 2D Subtitulado)
    """

    if not start_date:
        # Empezar desde hoy, pero ajustar al lunes si es necesario
        today = date.today()
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)

    # Generar las 7 fechas de la semana
    week_dates = []
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        week_dates.append({
            "date": current_date,
            "day_number": current_date.day,
            "day_name_short": ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"][current_date.weekday()],
            "month_short": ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                            "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"][current_date.month - 1],
            "is_today": current_date == date.today()
        })

    # Obtener todos los teatros
    theaters = db.query(Theater).filter(Theater.is_active == True).all()

    # Obtener horarios para toda la semana
    week_end = start_date + timedelta(days=6)
    showtimes = db.query(MovieShowtime).options(
        joinedload(MovieShowtime.movie),
        joinedload(MovieShowtime.theater)
    ).filter(
        MovieShowtime.show_date >= start_date,
        MovieShowtime.show_date <= week_end,
        MovieShowtime.is_active == True
    ).order_by(
        MovieShowtime.theater_id,
        MovieShowtime.movie_id,
        MovieShowtime.show_date,
        MovieShowtime.show_time
    ).all()

    # Organizar datos por teatro
    theaters_data = []

    for theater in theaters:
        theater_showtimes = [st for st in showtimes if st.theater_id == theater.id]

        # Agrupar por película
        movies_in_theater = {}
        for showtime in theater_showtimes:
            movie_id = showtime.movie_id
            if movie_id not in movies_in_theater:
                movies_in_theater[movie_id] = {
                    "movie": {
                        "id": showtime.movie.id,
                        "title": showtime.movie.title,
                        "director": showtime.movie.director,
                        "duration": showtime.movie.duration,
                        "rating": showtime.movie.rating,
                        "poster_url": showtime.movie.poster_url
                    },
                    "formats": {}
                }

            # Agrupar por formato
            format_key = showtime.format.value
            if format_key not in movies_in_theater[movie_id]["formats"]:
                movies_in_theater[movie_id]["formats"][format_key] = {
                    "format_name": format_display_name(showtime.format),
                    "times": []
                }

            movies_in_theater[movie_id]["formats"][format_key]["times"].append({
                "time": showtime.show_time,
                "date": showtime.show_date.isoformat(),
                "available_tickets": showtime.available_tickets,
                "capacity": showtime.capacity
            })

        theaters_data.append({
            "id": theater.id,
            "name": theater.name,
            "location": theater.location,
            "movies": list(movies_in_theater.values())
        })

    return {
        "week_dates": week_dates,
        "month_year": f"{week_dates[0]['month_short']} {start_date.year}",
        "theaters": theaters_data,
        "total_showtimes": len(showtimes)
    }


@router.get("/calendar/theater/{theater_name}", response_model=Dict[str, Any])
async def get_theater_calendar(
        theater_name: str,
        start_date: Optional[date] = Query(None, description="Fecha de inicio"),
        days: int = Query(7, ge=1, le=14, description="Cantidad de días"),
        db: Session = Depends(get_db)
):
    """
    Obtener calendario específico de un teatro (ej: Chipichape).

    Replica el formato de las imágenes donde se expande un teatro específico
    mostrando todas sus funciones organizadas por película y formato.
    """

    # Buscar teatro por nombre (case insensitive)
    theater = db.query(Theater).filter(
        Theater.name.ilike(f"%{theater_name}%"),
        Theater.is_active == True
    ).first()

    if not theater:
        return {"error": f"Teatro '{theater_name}' no encontrado"}

    if not start_date:
        start_date = date.today()

    end_date = start_date + timedelta(days=days - 1)

    # Obtener horarios del teatro
    showtimes = db.query(MovieShowtime).options(
        joinedload(MovieShowtime.movie)
    ).filter(
        MovieShowtime.theater_id == theater.id,
        MovieShowtime.show_date >= start_date,
        MovieShowtime.show_date <= end_date,
        MovieShowtime.is_active == True
    ).order_by(
        MovieShowtime.movie_id,
        MovieShowtime.show_date,
        MovieShowtime.show_time
    ).all()

    # Generar fechas
    dates = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        dates.append({
            "date": current_date,
            "day_number": current_date.day,
            "day_name": ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"][current_date.weekday()],
            "formatted": f"{current_date.day} {['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'][current_date.month - 1]}"
        })

    # Organizar por película y formato
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
                    "poster_url": showtime.movie.poster_url
                },
                "formats": {}
            }

        format_key = showtime.format.value
        if format_key not in movies_schedule[movie_id]["formats"]:
            movies_schedule[movie_id]["formats"][format_key] = {
                "format_display": format_display_name(showtime.format),
                "showtimes": []
            }

        movies_schedule[movie_id]["formats"][format_key]["showtimes"].append({
            "date": showtime.show_date.isoformat(),
            "time": showtime.show_time,
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
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "dates": dates,
        "movies": list(movies_schedule.values()),
        "total_showtimes": len(showtimes)
    }


@router.get("/calendar/movie/{movie_id}/schedule", response_model=Dict[str, Any])
async def get_movie_schedule_all_theaters(
        movie_id: int,
        start_date: Optional[date] = Query(None, description="Fecha de inicio"),
        days: int = Query(7, ge=1, le=14, description="Cantidad de días"),
        db: Session = Depends(get_db)
):
    """
    Obtener horarios de una película específica en todos los teatros.

    Útil para mostrar dónde y cuándo se puede ver una película específica.
    """

    # Verificar que la película existe
    movie = db.query(Movie).filter(Movie.id == movie_id, Movie.is_active == True).first()
    if not movie:
        return {"error": "Película no encontrada"}

    if not start_date:
        start_date = date.today()

    end_date = start_date + timedelta(days=days - 1)

    # Obtener todos los horarios de la película
    showtimes = db.query(MovieShowtime).options(
        joinedload(MovieShowtime.theater)
    ).filter(
        MovieShowtime.movie_id == movie_id,
        MovieShowtime.show_date >= start_date,
        MovieShowtime.show_date <= end_date,
        MovieShowtime.is_active == True
    ).order_by(
        MovieShowtime.theater_id,
        MovieShowtime.show_date,
        MovieShowtime.show_time
    ).all()

    # Organizar por teatro
    theaters_schedule = {}

    for showtime in showtimes:
        theater_id = showtime.theater_id
        theater_name = showtime.theater.name

        if theater_id not in theaters_schedule:
            theaters_schedule[theater_id] = {
                "theater": {
                    "id": theater_id,
                    "name": theater_name,
                    "location": showtime.theater.location
                },
                "formats": {}
            }

        format_key = showtime.format.value
        if format_key not in theaters_schedule[theater_id]["formats"]:
            theaters_schedule[theater_id]["formats"][format_key] = {
                "format_display": format_display_name(showtime.format),
                "showtimes": []
            }

        theaters_schedule[theater_id]["formats"][format_key]["showtimes"].append({
            "date": showtime.show_date.isoformat(),
            "formatted_date": showtime.show_date.strftime("%d %b"),
            "time": showtime.show_time,
            "available_tickets": showtime.available_tickets,
            "is_almost_full": showtime.available_tickets < 20
        })

    return {
        "movie": {
            "id": movie.id,
            "title": movie.title,
            "director": movie.director,
            "duration": movie.duration,
            "rating": movie.rating,
            "poster_url": movie.poster_url
        },
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "theaters": list(theaters_schedule.values()),
        "total_showtimes": len(showtimes)
    }


def format_display_name(format_enum: ShowtimeFormat) -> str:
    """Convertir formato enum a nombre display amigable"""
    format_names = {
        ShowtimeFormat.TWO_D_DUBBED: "2D Doblado",
        ShowtimeFormat.TWO_D_SUBTITLED: "2D Subtitulado",
        ShowtimeFormat.THREE_D: "3D",
        ShowtimeFormat.IMAX: "IMAX"
    }
    return format_names.get(format_enum, format_enum.value)

