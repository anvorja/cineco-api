# app/services/auth_service.py
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User, UserRole
from app.schemas.auth import UserRegister, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token
from app.services.email_service import EmailService
from app.utils.helpers import validate_email, validate_phone

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication operations"""

    @staticmethod
    async def register_user(db: Session, user_data: UserRegister) -> User:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Created user object

        Raises:
            HTTPException: If email already exists or validation fails
        """
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )

        if not validate_phone(user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone format. Use Colombian format: 3XXXXXXXXX"
            )

        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(user_data.password)

        user = User(
            email=user_data.email,
            phone=user_data.phone,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=hashed_password,
            role=UserRole.CUSTOMER  # Por defecto
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        try:
            await EmailService.send_welcome_email(user)
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")

        return user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            db: Database session
            login_data: Login credentials

        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(
            User.email == login_data.email,
            User.is_active == True
        ).first()

        if not user:
            return None

        if not verify_password(login_data.password, user.password_hash):
            return None

        return user

    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> dict:
        """
        Login user and generate JWT token.

        Args:
            db: Database session
            login_data: Login credentials

        Returns:
            Dictionary with access token and user data

        Raises:
            HTTPException: If credentials are invalid
        """
        user = AuthService.authenticate_user(db, login_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate JWT token
        access_token = create_access_token(subject=user.email)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    def logout_user(user: User) -> Dict[str, Any]:
        """
        Handle user logout.

        En JWT stateless, no hay mucho que hacer en el servidor,
        pero podemos logging y otros side effects.

        Args:
            user: Usuario que está cerrando sesión

        Returns:
            Dictionary with logout confirmation
        """
        # Log logout event
        logout_time = datetime.now()
        logger.info(f"User {user.email} logged out successfully at {logout_time}")

        # En una implementación más robusta podrías:
        # 1. Agregar el token a una blacklist
        # 2. Limpiar refresh tokens
        # 3. Invalidar sesiones activas
        # 4. Notificar a otros servicios

        return {
            "message": "Sesión cerrada exitosamente",
            "user_id": user.id,
            "logout_time": logout_time,
            "status": "success"
        }

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
