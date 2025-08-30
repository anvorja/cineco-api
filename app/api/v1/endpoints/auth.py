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
    Register a new customer account.

    - **email**: Valid email address (unique)
    - **phone**: Colombian phone number (3XXXXXXXXX format)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: Password (minimum 6 characters)

    Returns the created user information (without password).
    """
    user = await AuthService.register_user(db, user_data)
    return UserResponse.from_orm(user)


@router.post("/login", response_model=Token)
async def login(
        login_data: UserLogin,
        db: Session = Depends(get_db)
):
    """
    Authenticate user and get access token.

    - **email**: Registered email address
    - **password**: User password

    Returns JWT access token for API authentication.
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
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse.from_orm(current_user)


@router.get("/verify-token")
async def verify_token(
        current_user: User = Depends(get_current_user)
):
    """
    Verify if JWT token is valid.

    Returns user ID and email if token is valid.
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value
    }