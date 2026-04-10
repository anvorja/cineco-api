# app/services/movie_service.py
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import desc, or_, and_
from fastapi import HTTPException, status

from app.models import Movie, MovieStatus
from app.models.theater import Theater, TheaterMovie, MovieShowtime, ShowtimeFormat
from app.schemas.movie import MovieCreate, MovieUpdate


class MovieService:
    """Servicio para operaciones de películas con teatros y horarios"""

    @staticmethod
    def create_movie(db: Session, movie_data: MovieCreate) -> Movie:
        """Crear película básica (sin teatros por ahora)."""
        existing_movie = db.query(Movie).filter(
            Movie.title.ilike(movie_data.title.strip())
        ).first()

        if existing_movie:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Película con título '{movie_data.title}' ya existe"
            )

        movie = Movie(
            title=movie_data.title.strip(),
            description=movie_data.description.strip(),
            genre=movie_data.genre.strip(),
            duration=movie_data.duration,
            rating=movie_data.rating.upper(),
            price=movie_data.price,
            director=movie_data.director.strip(),
            country=movie_data.country.strip(),
            status=movie_data.status,
            is_presale=movie_data.is_presale,
            release_date=movie_data.release_date,
            max_capacity=movie_data.max_capacity,
            available_tickets=movie_data.available_tickets,
            poster_url=str(movie_data.poster_url),
            backdrop_url=str(movie_data.backdrop_url),
            detail_1_url=str(movie_data.detail_1_url),
            detail_2_url=str(movie_data.detail_2_url)
        )

        db.add(movie)
        db.commit()
        db.refresh(movie)

        # Asignar a teatros si se especifica
        if movie_data.theater_ids:
            MovieService.assign_movie_to_theaters(db, movie.id, movie_data.theater_ids)

        return movie

    @staticmethod
    def assign_movie_to_theaters(db: Session, movie_id: int, theater_ids: List[int]) -> List[TheaterMovie]:
        """Asignar película a teatros específicos"""
        theater_movies = []

        for theater_id in theater_ids:
            # Verificar si ya existe la relación
            existing = db.query(TheaterMovie).filter(
                TheaterMovie.theater_id == theater_id,
                TheaterMovie.movie_id == movie_id
            ).first()

            if not existing:
                theater_movie = TheaterMovie(
                    theater_id=theater_id,
                    movie_id=movie_id,
                    capacity=100,
                    available_tickets=100
                )
                db.add(theater_movie)
                theater_movies.append(theater_movie)

        db.commit()
        return theater_movies

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int, include_inactive: bool = False) -> Optional[Movie]:
        """Obtener película por ID"""
        query = db.query(Movie).filter(Movie.id == movie_id)

        if not include_inactive:
            query = query.filter(Movie.is_active == True)

        return query.first()

    @staticmethod
    def get_movies(
            db: Session,
            skip: int = 0,
            limit: int = 10,
            include_inactive: bool = False,
            search: Optional[str] = None,
            genre: Optional[str] = None,
            director: Optional[str] = None,
            country: Optional[str] = None,
            status: Optional[MovieStatus] = None,
            is_presale: Optional[bool] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            rating: Optional[str] = None,
            available_only: bool = True,
            theater_name: Optional[str] = None
    ) -> List[Movie]:
        """Obtener películas con filtros avanzados"""

        query = db.query(Movie).options(
            selectinload(Movie.theater_movies).selectinload(TheaterMovie.theater)
        )

        # Filtros básicos
        if not include_inactive:
            query = query.filter(Movie.is_active == True)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Movie.title.ilike(search_term),
                    Movie.description.ilike(search_term),
                    Movie.director.ilike(search_term)
                )
            )

        # Filtros específicos
        if genre:
            query = query.filter(Movie.genre.ilike(f"%{genre.strip()}%"))

        if director:
            query = query.filter(Movie.director.ilike(f"%{director.strip()}%"))

        if country:
            query = query.filter(Movie.country.ilike(f"%{country.strip()}%"))

        if status:
            query = query.filter(Movie.status == status)

        if is_presale is not None:
            query = query.filter(Movie.is_presale == is_presale)

        # Filtros de precio
        if min_price is not None:
            query = query.filter(Movie.price >= min_price)
        if max_price is not None:
            query = query.filter(Movie.price <= max_price)

        if rating:
            query = query.filter(Movie.rating == rating.upper())

        if available_only:
            query = query.filter(Movie.available_tickets > 0)
            # Solo mostrar películas en cartelera o próximos estrenos con preventa
            query = query.filter(
                or_(
                    Movie.status == MovieStatus.IN_THEATERS,
                    and_(Movie.status == MovieStatus.COMING_SOON, Movie.is_presale == True)
                )
            )

        # Filtro por teatro
        if theater_name:
            query = query.join(Movie.theater_movies).join(TheaterMovie.theater).filter(
                Theater.name.ilike(f"%{theater_name}%")
            )

        # Orden por fecha de creación (más nuevas primero)
        query = query.order_by(desc(Movie.created_at))

        return query.offset(skip).limit(limit).all()


    @staticmethod
    def update_movie(db: Session, movie_id: int, movie_data: MovieUpdate) -> Optional[Movie]:
        """Actualizar película"""
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return None

        # Actualizar solo campos proporcionados
        update_data = movie_data.model_dump(exclude_unset=True, exclude_none=True)

        for field, value in update_data.items():
            if hasattr(movie, field):
                if isinstance(value, str) and field not in ['poster_url', 'backdrop_url', 'detail_1_url', 'detail_2_url']:
                    value = value.strip()
                if field == "rating" and value:
                    value = value.upper()
                # Convertir HttpUrl a string para campos URL
                if field.endswith('_url') and hasattr(value, '__str__'):
                    value = str(value)
                setattr(movie, field, value)

        db.commit()
        db.refresh(movie)

        return movie

    @staticmethod
    def toggle_movie_status(db: Session, movie_id: int) -> Optional[Movie]:
        """Alternar estado activo/inactivo de película"""
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return None

        movie.is_active = not movie.is_active
        db.commit()
        db.refresh(movie)

        return movie

    @staticmethod
    def get_movie_with_showtimes(db: Session, movie_id: int, include_inactive: bool = False) -> Optional[Movie]:
        """Obtener película con horarios cargados"""
        query = db.query(Movie).options(
            joinedload(Movie.showtimes).joinedload(MovieShowtime.theater),
            joinedload(Movie.theater_movies).joinedload(TheaterMovie.theater)
        ).filter(Movie.id == movie_id)

        if not include_inactive:
            query = query.filter(Movie.is_active == True)

        return query.first()

    @staticmethod
    def get_movie_showtimes(
            db: Session,
            movie_id: int,
            theater_id: Optional[int] = None,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None
    ) -> List[MovieShowtime]:
        """Obtener horarios específicos de una película"""

        query = db.query(MovieShowtime).options(
            joinedload(MovieShowtime.theater)
        ).filter(
            MovieShowtime.movie_id == movie_id,
            MovieShowtime.is_active == True
        )

        if theater_id:
            query = query.filter(MovieShowtime.theater_id == theater_id)

        if start_date:
            query = query.filter(MovieShowtime.show_date >= start_date)
        else:
            # Por defecto, desde hoy
            query = query.filter(MovieShowtime.show_date >= date.today())

        if end_date:
            query = query.filter(MovieShowtime.show_date <= end_date)

        return query.order_by(MovieShowtime.show_date, MovieShowtime.show_time).all()

    @staticmethod
    def get_theaters_for_movie(db: Session, movie_id: int) -> List[Theater]:
        """Obtener todos los teatros donde se proyecta una película"""
        return db.query(Theater).join(TheaterMovie).filter(
            TheaterMovie.movie_id == movie_id,
            TheaterMovie.is_active == True,
            Theater.is_active == True
        ).all()

    @staticmethod
    def get_movies_coming_soon(db: Session, limit: int = 10) -> List[Movie]:
        """Obtener próximos estrenos"""
        return db.query(Movie).filter(
            Movie.status == MovieStatus.COMING_SOON,
            Movie.is_active == True
        ).order_by(Movie.release_date).limit(limit).all()

    @staticmethod
    def get_movies_in_presale(db: Session, limit: int = 10) -> List[Movie]:
        """Obtener películas en preventa"""
        return db.query(Movie).filter(
            Movie.is_presale == True,
            Movie.is_active == True
        ).order_by(Movie.release_date).limit(limit).all()

    @staticmethod
    def get_daily_schedule(db: Session, target_date: date) -> Dict[str, Any]:
        """Obtener programación completa de un día específico"""

        showtimes = db.query(MovieShowtime).options(
            joinedload(MovieShowtime.movie),
            joinedload(MovieShowtime.theater)
        ).filter(
            MovieShowtime.show_date == target_date,
            MovieShowtime.is_active == True
        ).order_by(MovieShowtime.show_time).all()

        # Agrupar por teatro
        theaters_schedule = {}
        for showtime in showtimes:
            theater_name = showtime.theater.name
            if theater_name not in theaters_schedule:
                theaters_schedule[theater_name] = {
                    "theater": {
                        "id": showtime.theater.id,
                        "name": theater_name,
                        "location": showtime.theater.location
                    },
                    "movies": {}
                }

            movie_title = showtime.movie.title
            if movie_title not in theaters_schedule[theater_name]["movies"]:
                theaters_schedule[theater_name]["movies"][movie_title] = {
                    "movie": {
                        "id": showtime.movie.id,
                        "title": movie_title,
                        "director": showtime.movie.director,
                        "duration": showtime.movie.duration,
                        "rating": showtime.movie.rating,
                        "poster_url": showtime.movie.poster_url
                    },
                    "showtimes": []
                }

            theaters_schedule[theater_name]["movies"][movie_title]["showtimes"].append({
                "id": showtime.id,
                "time": showtime.show_time,
                "format": showtime.format.value,
                "available_tickets": showtime.available_tickets,
                "capacity": showtime.capacity
            })

        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "formatted_date": target_date.strftime("%d-%b-%Y"),
            "theaters": list(theaters_schedule.values())
        }

    @staticmethod
    def create_showtimes_for_movie(
            db: Session,
            movie_id: int,
            start_date: date,
            days_count: int = 7,
            theater_ids: Optional[List[int]] = None
    ) -> List[MovieShowtime]:
        """Crear horarios específicos para una película"""

        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Película no encontrada")

        if not theater_ids:
            theater_ids = [tm.theater_id for tm in movie.theater_movies if tm.is_active]

        standard_times = [
            {"time": "12:30", "format": ShowtimeFormat.TWO_D_DUBBED},
            {"time": "15:20", "format": ShowtimeFormat.TWO_D_DUBBED},
            {"time": "18:10", "format": ShowtimeFormat.TWO_D_DUBBED},
            {"time": "21:00", "format": ShowtimeFormat.TWO_D_SUBTITLED},
        ]

        created_showtimes = []

        for day_offset in range(days_count):
            show_date = start_date + timedelta(days=day_offset)

            for theater_id in theater_ids:
                for schedule in standard_times:
                    # Verificar si ya existe
                    existing = db.query(MovieShowtime).filter(
                        MovieShowtime.movie_id == movie_id,
                        MovieShowtime.theater_id == theater_id,
                        MovieShowtime.show_date == show_date,
                        MovieShowtime.show_time == schedule["time"],
                        MovieShowtime.format == schedule["format"]
                    ).first()

                    if not existing:
                        showtime = MovieShowtime(
                            movie_id=movie_id,
                            theater_id=theater_id,
                            show_date=show_date,
                            show_time=schedule["time"],
                            format=schedule["format"],
                            capacity=100,
                            available_tickets=100
                        )
                        db.add(showtime)
                        created_showtimes.append(showtime)

        db.commit()
        return created_showtimes





