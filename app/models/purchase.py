# app/models/purchases.py
import enum
from sqlalchemy import String, Integer, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User
    from .movie import Movie


class PurchaseStatus(str, enum.Enum):
    """Enumeración de estados de la compra"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class TicketStatus(str, enum.Enum):
    """Enumeración de estados del boleto"""
    ACTIVE = "active"
    USED = "used"
    CANCELLED = "cancelled"


class Purchase(BaseModel):
    """
    Modelo de compra que representa una transacción de boletos.

    Atributos:
        user_id: ID del usuario que realizó la compra
        movie_id: ID de la película para la cual se compraron los boletos
        quantity: Cantidad de boletos comprados
        total_amount: Monto total pagado
        payment_info: Información de pago (JSON con detalles de tarjeta enmascarados)
        status: Estado de la compra (pending, confirmed, cancelled, refunded)
    """
    __tablename__ = "purchases"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    movie_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("movies.id"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[PurchaseStatus] = mapped_column(
        Enum(PurchaseStatus),
        default=PurchaseStatus.PENDING,
        nullable=False,
        index=True
    )

    # Relaciones
    user: Mapped["User"] = relationship(back_populates="purchases")
    movie: Mapped["Movie"] = relationship(back_populates="purchases")
    tickets: Mapped[List["Ticket"]] = relationship(
        back_populates="purchase",
        cascade="all, delete-orphan"
    )

    @property
    def is_confirmed(self) -> bool:
        """Verifica si la compra está confirmada"""
        return self.status == PurchaseStatus.CONFIRMED

    def __repr__(self) -> str:
        return f"<Purchase(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class Ticket(BaseModel):
    """
    Modelo de un boleto individual.

    Atributos:
        purchase_id: ID de la compra asociada
        ticket_code: Código único del boleto para validación
        seat_number: Asignación de asiento (GENERAL-X para MVP)
        status: Estado del boleto (active, used, cancelled)
    """
    __tablename__ = "tickets"

    purchase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchases.id"), nullable=False, index=True
    )
    ticket_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    seat_number: Mapped[str] = mapped_column(String(20), nullable=False)  # GENERAL-1, GENERAL-2, etc.
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus),
        default=TicketStatus.ACTIVE,
        nullable=False,
        index=True
    )

    # Relaciones
    purchase: Mapped["Purchase"] = relationship(back_populates="tickets")

    @property
    def is_active(self) -> bool:
        """Verifica si el boleto está activo"""
        return self.status == TicketStatus.ACTIVE

    def __repr__(self) -> str:
        return f"<Ticket(id={self.id}, code='{self.ticket_code}', status='{self.status}')>"