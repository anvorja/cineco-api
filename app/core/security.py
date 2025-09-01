# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
        subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crear un token de acceso JWT.

    Args:
        subject: Sujeto del token (generalmente ID o email del usuario)
        expires_delta: Tiempo de expiración del token

    Returns:
        Cadena del token JWT
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verificar un token JWT y extraer el sujeto.

    Args:
        token: Cadena del token JWT

    Returns:
        Sujeto del token si es válido, None en caso contrario
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = payload.get("sub")
        return token_data
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar una contraseña contra su hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña encriptada desde la base de datos

    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generar el hash de una contraseña.

    Args:
        password: Contraseña en texto plano

    Returns:
        Contraseña encriptada (hash)
    """
    return pwd_context.hash(password)
