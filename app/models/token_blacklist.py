# app/models/token_blacklist.py
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class TokenBlacklist(BaseModel):
    """
    Modelo para tokens JWT invalidados.

    Permite invalidar tokens inmediatamente sin esperar a que expiren.
    """
    __tablename__ = "token_blacklist"

    # El token completo (puede ser largo)
    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)

    # ID del usuario que tenía este token
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Cuándo se invalidó
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Razón de invalidación
    reason: Mapped[str] = mapped_column(
        String(100),
        default="logout",
        nullable=False
    )

    # Email del usuario (para auditoría)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<TokenBlacklist(user_id={self.user_id}, reason='{self.reason}')>"
