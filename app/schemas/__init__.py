# app/schemas/__init__.py
from .auth import UserRegister, UserLogin, Token, UserResponse
from .blacklist import BlacklistStats, BlacklistCleanupResponse, ForceLogoutResponse, TokenBlacklistResponse, \
    BlacklistListResponse
from .movie import MovieCreate, MovieUpdate, MovieResponse, MovieListResponse
from .purchase import PurchaseCreate, PurchaseResponse, PurchaseListResponse, PaymentInfo

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
    "MovieListResponse",

    # Purchase schemas
    "PurchaseCreate",
    "PurchaseResponse",
    "PurchaseListResponse",
    "PaymentInfo",

    # Blacklist schemas
    "BlacklistStats",
    "BlacklistCleanupResponse",
    "ForceLogoutResponse",
    "BlacklistListResponse",
    "TokenBlacklistResponse"
]