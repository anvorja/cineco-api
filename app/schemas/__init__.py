# app/schemas/__init__.py
from .auth import UserRegister, UserLogin, Token, UserResponse
from .movie import MovieCreate, MovieUpdate, MovieResponse, MovieListResponse

__all__ = [
    # Auth schemas
    "UserRegister",
    "UserLogin",
    "Token",
    "UserResponse",
    # Movie schemas
    "MovieCreate",
    "MovieUpdate",
    "MovieResponse",
    "MovieListResponse"
]