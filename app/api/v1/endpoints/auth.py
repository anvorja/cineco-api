# app/api/v1/endpoints/auth.py# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.api.dependencies import get_current_user
from app.models import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserRegister,
        db: Session = Depends(get_db)
):
    """
    Registrar una nueva cuenta de cliente.

    - **email**: Dirección de correo válida (única)
    - **phone**: Número de teléfono colombiano (formato 3XXXXXXXXX)
    - **first_name**: Nombre del usuario
    - **last_name**: Apellido del usuario
    - **password**: Contraseña (mínimo 6 caracteres)

    Retorna la información del usuario creado (sin contraseña).
    """
    user = await AuthService.register_user(db, user_data)
    return UserResponse.from_orm(user)


@router.post("/login", response_model=Token)
async def login(
        login_data: UserLogin,
        db: Session = Depends(get_db)
):
    """
    Autenticar al usuario y obtener un token de acceso.

    - **email**: Correo electrónico registrado
    - **password**: Contraseña del usuario

    Retorna un token JWT de acceso para autenticación en la API.
    """
    result = AuthService.login_user(db, login_data)
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """
    Obtener la información del usuario autenticado.

    Requiere un token JWT válido en el encabezado Authorization.
    """
    return UserResponse.from_orm(current_user)


@router.get("/verify-token")
async def verify_token(
        current_user: User = Depends(get_current_user)
):
    """
    Verificar si el token JWT es válido.

    Retorna el ID, correo y rol del usuario si el token es válido.
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value
    }