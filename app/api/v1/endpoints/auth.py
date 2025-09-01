# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse, LogoutResponse
from app.api.dependencies import get_current_user, get_current_token
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


@router.post("/logout", response_model=LogoutResponse)
async def logout(
        current_token: str = Depends(get_current_token),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Cerrar sesión invalidando el token inmediatamente mediante blacklist.

    ✅ INVALIDACIÓN INMEDIATA: El token se agrega a una blacklist
    ✅ SEGURIDAD MEJORADA: Token no se puede reutilizar
    ✅ AUDITORÍA: Se registra cuándo y quién hizo logout

    Requiere un token JWT válido en el encabezado Authorization.
    Una vez ejecutado, el token quedará inmediatamente invalidado.
    """
    # Agregar token a blacklist para invalidarlo inmediatamente
    success = TokenService.blacklist_token(
        db=db,
        token=current_token,
        user=current_user,
        reason="logout"
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing logout. Please try again."
        )

    return LogoutResponse(
        message="Sesión cerrada exitosamente. Token invalidado inmediatamente.",
        user_id=current_user.id,
        logout_time=None  # Se llenará automáticamente
    )


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
    Verificar si el token JWT es válido y no está en blacklist.

    Retorna el ID, correo y rol del usuario si el token es válido.
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value
    }


# Logout de todas las sesiones (TODO: en frontend)
@router.post("/logout-all")
async def logout_all_sessions(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Cerrar TODAS las sesiones activas del usuario.

    Útil para casos de seguridad donde el usuario quiere
    invalidar todos sus tokens activos.
    """
    count = TokenService.blacklist_all_user_tokens(
        db=db,
        user_id=current_user.id,
        reason="logout_all_sessions"
    )

    return {
        "message": "Todas las sesiones han sido cerradas exitosamente",
        "user_id": current_user.id,
        "sessions_closed": count
    }