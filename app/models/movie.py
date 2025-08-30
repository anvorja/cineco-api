# app/models/movie.py
from sqlalchemy import String, Text, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, TYPE_CHECKING

from .base import BaseModel

if TYPE_CHECKING:
    from .purchase import Purchase

class Movie(BaseModel):
    """
    Movie model representing films available for ticket purchase.

    Attributes:
        title: Movie title
        description: Detailed description of the movie
        genre: Movie genre (e.g., Action, Comedy, Drama)
        duration: Duration in minutes
        rating: Movie rating (G, PG, PG-13, R, NC-17)
        price: Ticket price in Colombian pesos
        max_capacity: Maximum tickets available (default 100 for MVP)
        available_tickets: Current available tickets
        image_url: URL to movie poster image (Cloudinary)
    """
    __tablename__ = "movies"

    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[str] = mapped_column(String(10), nullable=False)  # G, PG, PG-13, R, NC-17
    price: Mapped[float] = mapped_column(Float, nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    available_tickets: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relaciones
    purchases: Mapped[List["Purchase"]] = relationship(back_populates="movie")

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
        return (self.sold_tickets / self.max_capacity) * 100

    def can_purchase(self, quantity: int) -> bool:
        return self.is_available and self.available_tickets >= quantity

    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, title='{self.title}', available={self.available_tickets})>"