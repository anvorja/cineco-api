# app/models/movie.py
from datetime import date
from typing import List, TYPE_CHECKING
from urllib.parse import urlparse
import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import String, Integer, Float, Boolean, Date, Enum

from .base import BaseModel

if TYPE_CHECKING:
    from .purchase import Purchase
    from .theater import TheaterMovie, MovieShowtime


class MovieStatus(str, enum.Enum):
    """Estado de la película en cartelera"""
    IN_THEATERS = "in_theaters"
    COMING_SOON = "coming_soon"
    ENDED = "ended"


class Movie(BaseModel):
    __tablename__ = "movies"

    # --------- Campos básicos ---------
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[str] = mapped_column(String(10), nullable=False)  # G, PG, PG-13, R, NC-17
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # --------- NUEVOS CAMPOS ---------
    director: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    status: Mapped[MovieStatus] = mapped_column(
        Enum(MovieStatus),
        default=MovieStatus.IN_THEATERS,
        nullable=False,
        index=True
    )

    # Preventa
    is_presale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Fecha de estreno
    release_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # --------- Campos de capacidad ---------
    max_capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    available_tickets: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # --------- Imágenes obligatorias ---------
    poster_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    backdrop_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    detail_1_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    detail_2_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    # --------- Relaciones ---------
    purchases: Mapped[List["Purchase"]] = relationship(back_populates="movie")
    theater_movies: Mapped[List["TheaterMovie"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    showtimes: Mapped[List["MovieShowtime"]] = relationship(back_populates="movie", cascade="all, delete-orphan")

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

    # --------- Properties Básicas ---------
    @property
    def sold_tickets(self) -> int:
        return self.max_capacity - self.available_tickets

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

    # --------- NUEVAS PROPERTIES ---------
    @property
    def formatted_release_date(self) -> str:
        """Formato: 04-Sept-2025"""
        months = {
            1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Dic"
        }
        return f"{self.release_date.day:02d}-{months[self.release_date.month]}-{self.release_date.year}"

    @property
    def is_in_theaters(self) -> bool:
        """Está en cartelera actualmente"""
        return self.status == MovieStatus.IN_THEATERS

    @property
    def is_coming_soon(self) -> bool:
        """Es próximo estreno"""
        return self.status == MovieStatus.COMING_SOON

    @property
    def theaters(self) -> List[str]:
        """Lista de nombres de teatros donde se proyecta"""
        return [tm.theater.name for tm in self.theater_movies if tm.is_active]

    @property
    def is_available(self) -> bool:
        """
        Película disponible para mostrar en listings públicos.

        Una película se muestra si:
        - Está activa
        - Tiene tickets disponibles
        - Está en cartelera O es próximo estreno con preventa
        """
        if not self.is_active or self.available_tickets <= 0:
            return False

        # En cartelera: siempre disponible para mostrar
        if self.status == MovieStatus.IN_THEATERS:
            return True

        # Próximo estreno: solo si tiene preventa habilitada
        if self.status == MovieStatus.COMING_SOON and self.is_presale:
            return True

        return False

    def can_purchase(self, quantity: int) -> bool:
        """
        Verificar si se pueden comprar tickets.

        LÓGICA CORREGIDA:
        - En cartelera: SIEMPRE se puede comprar
        - Próximo estreno + preventa: SÍ se puede comprar (venta anticipada)
        - Próximo estreno sin preventa: NO se puede comprar aún
        - Finalizada: NO se puede comprar
        """
        if not self.is_active or quantity <= 0 or self.available_tickets < quantity:
            return False

        # Películas en cartelera: siempre se puede comprar
        if self.status == MovieStatus.IN_THEATERS:
            return True

        # Próximo estreno: solo si está en preventa
        if self.status == MovieStatus.COMING_SOON and self.is_presale:
            return True

        # En cualquier otro caso: no se puede comprar
        return False

    def get_purchase_availability_info(self) -> dict:
        """Información detallada sobre disponibilidad de compra"""
        if self.status == MovieStatus.IN_THEATERS:
            return {
                "can_purchase": self.available_tickets > 0,
                "status": "En cartelera",
                "message": "¡Ya disponible en cines!" if self.available_tickets > 0 else "Entradas agotadas"
            }
        elif self.status == MovieStatus.COMING_SOON:
            if self.is_presale:
                return {
                    "can_purchase": self.available_tickets > 0,
                    "status": "Preventa",
                    "message": f"Preventa disponible - Estreno: {self.formatted_release_date}"
                }
            else:
                return {
                    "can_purchase": False,
                    "status": "Próximo estreno",
                    "message": f"Próximamente - Estreno: {self.formatted_release_date}"
                }
        else:  # ENDED
            return {
                "can_purchase": False,
                "status": "Finalizada",
                "message": "Ya no está en cartelera"
            }
