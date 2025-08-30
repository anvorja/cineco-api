# app/schemas/auth.py
from pydantic import BaseModel, Field, EmailStr

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User email address")
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")

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
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "juan.perez@email.com",
                "password": "secreto123"
            }
        }
    }


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class UserResponse(BaseModel):
    """Schema for user data response"""
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
        """Create response from User model"""
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
