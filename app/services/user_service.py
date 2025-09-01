# app/services/user_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserUpdate


class UserService:
    """Service for user operations"""

    @staticmethod
    async def update_profile(db: Session, user_id: int, profile_data: UserUpdate) -> User:
        """
        Actualizar el perfil del usuario.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Actualizar solo los campos que se proporcionaron
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    async def change_password(
            db: Session,
            user_id: int,
            current_password: str,
            new_password: str
    ):
        """
        Cambiar la contraseña del usuario.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verificar contraseña actual
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

        # Actualizar contraseña
        user.password_hash = get_password_hash(new_password)
        db.commit()

    @staticmethod
    async def delete_account(db: Session, user_id: int):
        """
        Eliminar la cuenta del usuario.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # En lugar de eliminar, marcar como inactivo
        # user.is_active = False
        # db.commit()

        # O eliminar completamente si prefieres:
        db.delete(user)
        db.commit()
