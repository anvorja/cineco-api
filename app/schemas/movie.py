# app/schemas/movie.py
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, date
from enum import Enum


class MovieStatus(str, Enum):
    """Estado de la película"""
    IN_THEATERS = "in_theaters"
    COMING_SOON = "coming_soon"
    ENDED = "ended"


class ShowtimeFormat(str, Enum):
    """Formato de proyección"""
    TWO_D_DUBBED = "2d_dubbed"
    TWO_D_SUBTITLED = "2d_subtitled"
    THREE_D = "3d"
    IMAX = "imax"


class MovieBase(BaseModel):
    """Esquema base para película"""
    title: str = Field(..., min_length=1, max_length=200, description="Título de la película")
    description: str = Field(..., min_length=10, max_length=1000, description="Descripción de la película")
    genre: str = Field(..., min_length=1, max_length=50, description="Género de la película")
    duration: int = Field(..., gt=0, le=600, description="Duración en minutos")
    rating: str = Field(..., pattern="^(G|PG|PG-13|R|NC-17)$", description="Clasificación")
    price: float = Field(..., gt=0, le=100000, description="Precio del ticket en pesos colombianos")
    director: str = Field(..., min_length=1, max_length=200, description="Director de la película")
    country: str = Field(..., min_length=1, max_length=100, description="País de origen")
    status: MovieStatus = Field(default=MovieStatus.IN_THEATERS, description="Estado en cartelera")
    is_presale: bool = Field(default=False, description="Si está en preventa")
    release_date: date = Field(..., description="Fecha de estreno")

    # Imágenes obligatorias
    poster_url: HttpUrl = Field(..., description="Imagen principal (vista de lista)")
    backdrop_url: HttpUrl = Field(..., description="Imagen de fondo (vista de detalle)")
    detail_1_url: HttpUrl = Field(..., description="Imagen de detalle 1")
    detail_2_url: HttpUrl = Field(..., description="Imagen de detalle 2")


class MovieCreate(MovieBase):
    """Esquema para creación de película"""
    max_capacity: int = Field(default=100, ge=1, le=500, description="Capacidad máxima")
    available_tickets: int = Field(default=100, ge=0, le=500, description="Tickets disponibles")

    # Teatros donde se proyectará (opcional)
    theater_ids: Optional[List[int]] = Field(default=None, description="IDs de teatros específicos")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Un Poeta",
                "description": "La obsesión de Óscar Restrepo por la poesía...",
                "genre": "Comedia",
                "duration": 120,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Iván D. Gaona",
                "country": "Colombia",
                "status": "in_theaters",
                "is_presale": False,
                "release_date": "2025-09-04",
                "max_capacity": 100,
                "available_tickets": 100,
                "poster_url": "https://example.com/poster.jpg",
                "backdrop_url": "https://example.com/backdrop.jpg",
                "detail_1_url": "https://example.com/detail1.jpg",
                "detail_2_url": "https://example.com/detail2.jpg",
                "theater_ids": [1, 2, 3, 4, 5]
            }
        }
    }


class MovieUpdate(BaseModel):
    """Esquema para actualización de película"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    duration: Optional[int] = Field(None, gt=0, le=600)
    rating: Optional[str] = Field(None, pattern="^(G|PG|PG-13|R|NC-17)$")
    price: Optional[float] = Field(None, gt=0, le=100000)
    director: Optional[str] = Field(None, min_length=1, max_length=200)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[MovieStatus] = None
    is_presale: Optional[bool] = None
    release_date: Optional[date] = None

    max_capacity: Optional[int] = Field(None, ge=1, le=500)
    available_tickets: Optional[int] = Field(None, ge=0, le=500)

    # Imágenes opcionales al actualizar
    poster_url: Optional[HttpUrl] = None
    backdrop_url: Optional[HttpUrl] = None
    detail_1_url: Optional[HttpUrl] = None
    detail_2_url: Optional[HttpUrl] = None


class TheaterBase(BaseModel):
    """Schema base para teatro"""
    name: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)


class TheaterCreate(TheaterBase):
    """Esquema para creación de teatro"""
    pass


class TheaterResponse(TheaterBase):
    """Esquema para respuesta de teatro"""
    id: int
    is_active: bool
    created_at: datetime

    @classmethod
    def from_orm(cls, theater):
        return cls(
            id=theater.id,
            name=theater.name,
            location=theater.location,
            description=theater.description,
            is_active=theater.is_active,
            created_at=theater.created_at
        )


class ShowtimeResponse(BaseModel):
    """Esquema para horarios de proyección"""
    id: int
    show_date: date
    show_time: str
    format: ShowtimeFormat
    capacity: int
    available_tickets: int
    theater_name: str

    @classmethod
    def from_orm(cls, showtime):
        return cls(
            id=showtime.id,
            show_date=showtime.show_date,
            show_time=showtime.show_time,
            format=showtime.format,
            capacity=showtime.capacity,
            available_tickets=showtime.available_tickets,
            theater_name=showtime.theater.name
        )


class MovieResponse(BaseModel):
    """Esquema para respuesta detallada de película"""
    id: int
    title: str
    description: str
    genre: str
    duration: int
    rating: str
    price: float
    director: str
    country: str
    status: str
    is_presale: bool
    release_date: date
    formatted_release_date: str

    max_capacity: int
    available_tickets: int
    is_active: bool
    created_at: datetime

    poster_url: str
    backdrop_url: str
    detail_1_url: str
    detail_2_url: str

    sold_tickets: int
    is_available: bool
    occupancy_rate: float
    detail_images: List[str]
    all_image_urls: List[str]

    theaters: List[str]
    is_in_theaters: bool
    is_coming_soon: bool

    @classmethod
    def from_orm(cls, movie):
        return cls(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            genre=movie.genre,
            duration=movie.duration,
            rating=movie.rating,
            price=movie.price,
            director=movie.director,
            country=movie.country,
            status=movie.status.value,
            is_presale=movie.is_presale,
            release_date=movie.release_date,
            formatted_release_date=movie.formatted_release_date,
            max_capacity=movie.max_capacity,
            available_tickets=movie.available_tickets,
            is_active=movie.is_active,
            created_at=movie.created_at,
            poster_url=movie.poster_url,
            backdrop_url=movie.backdrop_url,
            detail_1_url=movie.detail_1_url,
            detail_2_url=movie.detail_2_url,
            sold_tickets=movie.sold_tickets,
            is_available=movie.is_available,
            occupancy_rate=movie.occupancy_rate,
            detail_images=movie.detail_images,
            all_image_urls=movie.all_image_urls,
            theaters=movie.theaters,
            is_in_theaters=movie.is_in_theaters,
            is_coming_soon=movie.is_coming_soon
        )


class MovieWithShowtimesResponse(MovieResponse):
    """Esquema para película con horarios asociados"""
    showtimes: List[ShowtimeResponse]

    @classmethod
    def from_orm(cls, movie):
        base_data = MovieResponse.from_orm(movie).model_dump()
        base_data['showtimes'] = [ShowtimeResponse.from_orm(st) for st in movie.showtimes if st.is_active]
        return cls(**base_data)


class MovieListResponse(BaseModel):
    """Esquema para lista compacta de películas"""
    id: int
    title: str
    genre: str
    duration: int
    rating: str
    price: float
    director: str
    country: str
    status: str
    is_presale: bool
    formatted_release_date: str
    available_tickets: int
    is_available: bool
    occupancy_rate: float
    theaters: List[str]

    # Solo poster para la lista
    poster_url: str

    @classmethod
    def from_orm(cls, movie):
        return cls(
            id=movie.id,
            title=movie.title,
            genre=movie.genre,
            duration=movie.duration,
            rating=movie.rating,
            price=movie.price,
            director=movie.director,
            country=movie.country,
            status=movie.status.value,
            is_presale=movie.is_presale,
            formatted_release_date=movie.formatted_release_date,
            available_tickets=movie.available_tickets,
            is_available=movie.is_available,
            occupancy_rate=movie.occupancy_rate,
            theaters=movie.theaters,
            poster_url=movie.poster_url
        )


# Schema para crear horarios masivamente
class CreateShowtimesRequest(BaseModel):
    """Esquema para crear horarios masivamente"""
    movie_id: int
    start_date: date
    days_count: int = Field(default=7, ge=1, le=30, description="Cantidad de días a programar")
    theater_ids: Optional[List[int]] = Field(default=None, description="Teatros específicos o todos")

    model_config = {
        "json_schema_extra": {
            "example": {
                "movie_id": 1,
                "start_date": "2025-09-03",
                "days_count": 7,
                "theater_ids": [1, 2, 3, 4, 5]
            }
        }
    }