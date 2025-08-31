# app/schemas/movie.py
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class MovieBase(BaseModel):
    """Base schema for movie"""
    title: str = Field(..., min_length=1, max_length=200, description="Movie title")
    description: str = Field(..., min_length=10, max_length=1000, description="Movie description")
    genre: str = Field(..., min_length=1, max_length=50, description="Movie genre")
    duration: int = Field(..., gt=0, le=600, description="Duration in minutes")
    rating: str = Field(..., pattern="^(G|PG|PG-13|R|NC-17)$", description="Movie rating")
    price: float = Field(..., gt=0, le=100000, description="Ticket price in Colombian pesos")

    # Imágenes obligatorias
    poster_url: HttpUrl = Field(..., description="Main poster image (list view)")
    backdrop_url: HttpUrl = Field(..., description="Backdrop image (detail view)")
    detail_1_url: HttpUrl = Field(..., description="Detail image 1")
    detail_2_url: HttpUrl = Field(..., description="Detail image 2")


class MovieCreate(MovieBase):
    """Schema for creating a movie (admin only)"""
    max_capacity: int = Field(default=100, ge=1, le=500, description="Maximum tickets")
    available_tickets: int = Field(default=100, ge=0, le=500, description="Available tickets")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Avatar: El Camino del Agua",
                "description": "Secuela épica de la película Avatar donde Jake y Neytiri exploran nuevos territorios acuáticos de Pandora.",
                "genre": "Ciencia Ficción",
                "duration": 192,
                "rating": "PG-13",
                "price": 15000.0,
                "max_capacity": 100,
                "available_tickets": 100,
                "poster_url": "https://res.cloudinary.com/example/avatar2-poster.jpg",
                "backdrop_url": "https://res.cloudinary.com/example/avatar2-backdrop.jpg",
                "detail_1_url": "https://res.cloudinary.com/example/avatar2-detail1.jpg",
                "detail_2_url": "https://res.cloudinary.com/example/avatar2-detail2.jpg"
            }
        }
    }


class MovieUpdate(BaseModel):
    """Schema for updating a movie (admin only)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    duration: Optional[int] = Field(None, gt=0, le=600)
    rating: Optional[str] = Field(None, pattern="^(G|PG|PG-13|R|NC-17)$")
    price: Optional[float] = Field(None, gt=0, le=100000)
    max_capacity: Optional[int] = Field(None, ge=1, le=500)
    available_tickets: Optional[int] = Field(None, ge=0, le=500)

    # Imágenes opcionales al actualizar
    poster_url: Optional[HttpUrl] = None
    backdrop_url: Optional[HttpUrl] = None
    detail_1_url: Optional[HttpUrl] = None
    detail_2_url: Optional[HttpUrl] = None


class MovieResponse(BaseModel):
    """Schema for movie response"""
    id: int
    title: str
    description: str
    genre: str
    duration: int
    rating: str
    price: float
    max_capacity: int
    available_tickets: int
    is_active: bool
    created_at: datetime

    # Imágenes
    poster_url: str
    backdrop_url: str
    detail_1_url: str
    detail_2_url: str

    # Computed fields
    sold_tickets: int
    is_available: bool
    occupancy_rate: float
    detail_images: List[str]
    all_image_urls: List[str]

    @classmethod
    def from_orm(cls, movie):
        """Create response from Movie model"""
        return cls(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            genre=movie.genre,
            duration=movie.duration,
            rating=movie.rating,
            price=movie.price,
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
            all_image_urls=movie.all_image_urls
        )


class MovieListResponse(BaseModel):
    """Schema for movie list (public)"""
    id: int
    title: str
    genre: str
    duration: int
    rating: str
    price: float
    available_tickets: int
    is_available: bool
    occupancy_rate: float

    # Para la lista solo mostramos el poster principal
    poster_url: str

    @classmethod
    def from_orm(cls, movie):
        """Create list response from Movie model"""
        return cls(
            id=movie.id,
            title=movie.title,
            genre=movie.genre,
            duration=movie.duration,
            rating=movie.rating,
            price=movie.price,
            available_tickets=movie.available_tickets,
            is_available=movie.is_available,
            occupancy_rate=movie.occupancy_rate,
            poster_url=movie.poster_url
        )
