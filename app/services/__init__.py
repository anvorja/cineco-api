# app/services/__init__.py
from .auth_service import AuthService
from .movie_service import MovieService

__all__ = [
    "AuthService",
    "MovieService"
]