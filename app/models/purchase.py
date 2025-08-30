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
    """Purchase status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class TicketStatus(str, enum.Enum):
    """Ticket status enumeration"""
    ACTIVE = "active"
    USED = "used"
    CANCELLED = "cancelled"


class Purchase(BaseModel):
    """
    Purchase model representing a ticket purchase transaction.

    Attributes:
        user_id: ID of the user who made the purchase
        movie_id: ID of the movie for which tickets were purchased
        quantity: Number of tickets purchased
        total_amount: Total amount paid
        payment_info: Payment information (JSON with masked card details)
        status: Purchase status (pending, confirmed, cancelled, refunded)
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

    # Relationships
    user: Mapped["User"] = relationship(back_populates="purchases")
    movie: Mapped["Movie"] = relationship(back_populates="purchases")
    tickets: Mapped[List["Ticket"]] = relationship(
        back_populates="purchase",
        cascade="all, delete-orphan"
    )

    @property
    def is_confirmed(self) -> bool:
        """Check if purchase is confirmed"""
        return self.status == PurchaseStatus.CONFIRMED

    def __repr__(self) -> str:
        return f"<Purchase(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class Ticket(BaseModel):
    """
    Individual ticket model.

    Attributes:
        purchase_id: ID of the associated purchase
        ticket_code: Unique ticket code for validation
        seat_number: Seat assignment (GENERAL-X for MVP)
        status: Ticket status (active, used, cancelled)
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

    # Relationships
    purchase: Mapped["Purchase"] = relationship(back_populates="tickets")

    @property
    def is_active(self) -> bool:
        """Check if ticket is active"""
        return self.status == TicketStatus.ACTIVE

    def __repr__(self) -> str:
        return f"<Ticket(id={self.id}, code='{self.ticket_code}', status='{self.status}')>"