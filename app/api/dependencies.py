# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models import User

# Security scheme
security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """
    Obtener el usuario autenticado actual a partir del token JWT.

    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos

    Returns:
        Objeto del usuario autenticado

    Raises:
        HTTPException: Si el token no es válido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verificar el token
    user_email = verify_token(credentials.credentials)
    if user_email is None:
        raise credentials_exception

    # Buscar usuario en la base de datos
    user = db.query(User).filter(User.email == user_email).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtener el usuario actual y verificar si tiene rol de administrador.

    Args:
        current_user: Usuario autenticado actual

    Returns:
        Usuario administrador actual

    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtener el usuario actual y verificar si está activo.

    Args:
        current_user: Usuario autenticado actual

    Returns:
        Usuario activo actual

    Raises:
        HTTPException: Si el usuario no está activo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
