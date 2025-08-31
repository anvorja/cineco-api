# app/models/movie.py
from datetime import datetime
from typing import List, TYPE_CHECKING
from urllib.parse import urlparse

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import String, Integer, Float, Boolean, DateTime, func

from .base import BaseModel

if TYPE_CHECKING:
    from .purchase import Purchase


class Movie(BaseModel):
    """Movie model representing films available for ticket purchase."""
    __tablename__ = "movies"

    # --------- Campos básicos ---------
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[str] = mapped_column(String(10), nullable=False)  # G, PG, PG-13, R, NC-17
    price: Mapped[float] = mapped_column(Float, nullable=False)

    max_capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    available_tickets: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # --------- Imágenes obligatorias ---------
    poster_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    backdrop_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    detail_1_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    detail_2_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    # --------- Extras ---------
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # --------- Relaciones ---------
    purchases: Mapped[List["Purchase"]] = relationship(back_populates="movie")

    # --------- Validaciones ---------
    @validates('poster_url', 'backdrop_url', 'detail_1_url', 'detail_2_url')
    def validate_image_url(self, key: str, url: str) -> str:
        """Validar que la URL sea https y termine en una extensión de imagen válida"""
        if not url:
            raise ValueError(f"{key} es obligatorio")

        parsed = urlparse(url)

        if parsed.scheme != "https":
            raise ValueError(f"{key} debe usar HTTPS")

        if not url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            raise ValueError(f"{key} debe ser una imagen válida (jpg, jpeg, png, webp)")

        return url

    # --------- Helpers ---------
    @property
    def sold_tickets(self) -> int:
        return self.max_capacity - self.available_tickets

    @property
    def is_available(self) -> bool:
        return self.available_tickets > 0 and self.is_active

    @property
    def occupancy_rate(self) -> float:
        if self.max_capacity == 0:
            return 0.0
        return round((self.sold_tickets / self.max_capacity) * 100, 2)

    @property
    def detail_images(self) -> list[str]:
        """Devuelve solo las imágenes de detalle"""
        return [self.detail_1_url, self.detail_2_url]

    @property
    def all_image_urls(self) -> list[str]:
        """Devuelve todas las imágenes de la película"""
        return [
            self.poster_url,
            self.backdrop_url,
            self.detail_1_url,
            self.detail_2_url
        ]

    def can_purchase(self, quantity: int) -> bool:
        """
        Verificar si se pueden comprar la cantidad de tickets solicitada.

        Args:
            quantity: Número de tickets que se quieren comprar

        Returns:
            True si se pueden comprar, False caso contrario
        """
        return (
                self.is_active and
                self.available_tickets >= quantity > 0
        )