# app/schemas/auth.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class UserRegister(BaseModel):
    """Esquema para registro de usuario"""
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    phone: str = Field(..., min_length=10, max_length=20, description="Número de teléfono")
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "juan.perez@email.com",
                "phone": "3201234567",
                "first_name": "Juan",
                "last_name": "Pérez",
                "password": "secreto123"
            }
        }
    }


class UserLogin(BaseModel):
    """Esquema para inicio de sesión"""
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., description="Contraseña del usuario")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "juan.perez@email.com",
                "password": "secreto123"
            }
        }
    }


class Token(BaseModel):
    """Esquema para respuesta con token JWT"""
    access_token: str = Field(..., description="Token de acceso JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class LogoutResponse(BaseModel):
    """Esquema para respuesta de logout"""
    message: str = Field(..., description="Mensaje de confirmación")
    user_id: int = Field(..., description="ID del usuario que cerró sesión")
    logout_time: Optional[datetime] = Field(default_factory=datetime.now, description="Tiempo de cierre de sesión")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Sesión cerrada exitosamente",
                "user_id": 1,
                "logout_time": "2024-09-03T14:30:00"
            }
        }
    }

class UserResponse(BaseModel):
    """Esquema para respuesta con datos de usuario"""
    id: int
    email: str
    phone: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    full_name: str

    @classmethod
    def from_orm(cls, user):
        """Crear respuesta a partir del modelo User"""
        return cls(
            id=user.id,
            email=user.email,
            phone=user.phone,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            full_name=user.full_name
        )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "juan.perez@email.com",
                "phone": "3201234567",
                "first_name": "Juan",
                "last_name": "Pérez",
                "role": "customer",
                "is_active": True,
                "full_name": "Juan Pérez"
            }
        }
    }