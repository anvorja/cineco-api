# app/models/theater.py - CORREGIDO Y COMPLETO
from typing import List, TYPE_CHECKING
from datetime import datetime, date
import enum
from sqlalchemy import String, Integer, ForeignKey, Index, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .movie import Movie


class ShowtimeFormat(str, enum.Enum):
    """Formato de proyección"""
    TWO_D_DUBBED = "2d_dubbed"  # 2D Doblado
    TWO_D_SUBTITLED = "2d_subtitled"  # 2D Subtitulado
    THREE_D = "3d"  # 3D
    IMAX = "imax"  # IMAX


class Theater(BaseModel):
    """Modelo para teatros/salas de cine"""
    __tablename__ = "theaters"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relaciones
    theater_movies: Mapped[List["TheaterMovie"]] = relationship(
        back_populates="theater",
        cascade="all, delete-orphan"
    )
    showtimes: Mapped[List["MovieShowtime"]] = relationship(
        back_populates="theater",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Theater(id={self.id}, name='{self.name}')>"


class TheaterMovie(BaseModel):
    """Relación entre teatros y películas"""
    __tablename__ = "theater_movies"

    theater_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("theaters.id"), nullable=False, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), nullable=False, index=True
    )

    # Capacidad específica por teatro-película
    capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    available_tickets: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Relaciones
    theater: Mapped["Theater"] = relationship(back_populates="theater_movies")
    movie: Mapped["Movie"] = relationship(back_populates="theater_movies")

    # Índice compuesto para evitar duplicados
    __table_args__ = (
        Index('ix_theater_movie', 'theater_id', 'movie_id', unique=True),
    )

    def __repr__(self) -> str:
        return f"<TheaterMovie(theater_id={self.theater_id}, movie_id={self.movie_id})>"


class MovieShowtime(BaseModel):
    """Horarios específicos por película, teatro y fecha"""
    __tablename__ = "movie_showtimes"

    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), nullable=False, index=True
    )
    theater_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("theaters.id"), nullable=False, index=True
    )

    # Fecha específica de la función
    show_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Hora de la función
    show_time: Mapped[str] = mapped_column(String(10), nullable=False)

    # Formato de proyección
    format: Mapped[ShowtimeFormat] = mapped_column(Enum(ShowtimeFormat), nullable=False)

    # Capacidad para esta función específica
    capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    available_tickets: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Relaciones
    movie: Mapped["Movie"] = relationship(back_populates="showtimes")
    theater: Mapped["Theater"] = relationship(back_populates="showtimes")

    # Índice compuesto para evitar horarios duplicados
    __table_args__ = (
        Index('ix_showtime_unique', 'movie_id', 'theater_id', 'show_date', 'show_time', 'format', unique=True),
    )

    @property
    def datetime_show(self) -> datetime:
        """Combina fecha y hora para obtener datetime completo"""
        hour, minute = map(int, self.show_time.split(':'))
        return datetime.combine(self.show_date, datetime.min.time().replace(hour=hour, minute=minute))

    @property
    def is_available(self) -> bool:
        """Verifica si hay tickets disponibles para esta función"""
        return self.available_tickets > 0 and self.is_active

    def __repr__(self) -> str:
        return f"<MovieShowtime(movie_id={self.movie_id}, theater_id={self.theater_id}, date='{self.show_date}', time='{self.show_time}')>"
