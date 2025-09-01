# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.user import UserUpdate, PasswordChange
from app.services.user_service import UserService
from app.models import User

router = APIRouter()

@router.put("/profile")
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar el perfil del usuario autenticado.
    """
    updated_user = await UserService.update_profile(db, current_user.id, profile_data)
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": updated_user.id,
            "email": updated_user.email,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "phone": updated_user.phone,
            "full_name": updated_user.full_name
        }
    }

@router.put("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar la contraseña del usuario autenticado.
    """
    await UserService.change_password(
        db,
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password changed successfully"}

@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar la cuenta del usuario autenticado.
    """
    await UserService.delete_account(db, current_user.id)
    return {"message": "Account deleted successfully"}
