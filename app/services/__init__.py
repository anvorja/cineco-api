# app/services/__init__.py
from .auth_service import AuthService
from .movie_service import MovieService
from .purchase_service import PurchaseService
from .email_service import EmailService

__all__ = [
    "AuthService",
    "MovieService",
    "PurchaseService",
    "EmailService"
]