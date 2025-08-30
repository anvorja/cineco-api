# app/models/user.py
import enum
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from .base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(BaseModel):
    """
    User model for both customers and administrators.

    Attributes:
        email: Unique email address for authentication
        phone: Phone number for contact
        first_name: User's first name
        last_name: User's last name
        password_hash: Hashed password for security
        role: User role (admin/customer)
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.CUSTOMER, nullable=False
    )

    # Relationships (TYPE_CHECKING para evitar circular imports)
    if False:  # TYPE_CHECKING
        from .purchase import Purchase
        purchases: Mapped[List["Purchase"]] = relationship(back_populates="user")

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"