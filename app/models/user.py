# app/models/user.py
import enum
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from .base import BaseModel

if TYPE_CHECKING:
    from .purchase import Purchase

class UserRole(str, enum.Enum):
    """Enumeración de roles de usuario"""
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(BaseModel):
    """
    Modelo de usuario para clientes y administradores.

    Atributos:
        email: Dirección de correo única para autenticación
        phone: Número de teléfono de contacto
        first_name: Nombre del usuario
        last_name: Apellido del usuario
        password_hash: Contraseña hasheada para seguridad
        role: Rol del usuario (admin/customer)
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

    # Relaciones - usa anotación de tipo string
    purchases: Mapped[List["Purchase"]] = relationship(back_populates="user")

    @property
    def full_name(self) -> str:
        """Obtener nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        """Verificar si el usuario es administrador"""
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"