# app/schemas/user.py
from pydantic import BaseModel, Field
from typing import Optional

class UserUpdate(BaseModel):
    """Esquema para actualización de perfil de usuario"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)

class PasswordChange(BaseModel):
    """Esquema para cambio de contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")
    