# app/api/v1/endpoints/admin.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_admin
from app.services.movie_service import MovieService
from app.schemas.movie import MovieCreate, MovieUpdate, MovieResponse
from app.schemas.auth import UserResponse
from app.models import User, Movie

router = APIRouter()


# Movie Management
@router.post("/movies", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
        movie_data: MovieCreate,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Create a new movie (admin only).

    Requires admin authentication.
    Creates a new movie with the provided information.
    """
    movie = MovieService.create_movie(db=db, movie_data=movie_data)
    return MovieResponse.from_orm(movie)


@router.get("/movies", response_model=List[MovieResponse])
async def get_all_movies_admin(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
        include_inactive: bool = Query(default=False, description="Include inactive movies"),
        search: Optional[str] = Query(None, description="Search in title and description"),
        genre: Optional[str] = Query(None, description="Filter by genre"),
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Get all movies including inactive ones (admin only).

    Allows administrators to see all movies in the system,
    including inactive/disabled movies.
    """
    movies = MovieService.get_movies(
        db=db,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
        search=search,
        genre=genre,
        available_only=False  # Admin can see all movies
    )

    return [MovieResponse.from_orm(movie) for movie in movies]


@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie_admin(
        movie_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Get movie details including inactive movies (admin only).

    Administrators can view any movie, even inactive ones.
    """
    movie = MovieService.get_movie_by_id(db=db, movie_id=movie_id, include_inactive=True)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    return MovieResponse.from_orm(movie)


@router.put("/movies/{movie_id}", response_model=MovieResponse)
async def update_movie(
        movie_id: int,
        movie_data: MovieUpdate,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Update movie information (admin only).

    Allows administrators to modify movie details.
    Only provided fields will be updated.
    """
    movie = MovieService.update_movie(db=db, movie_id=movie_id, movie_data=movie_data)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    return MovieResponse.from_orm(movie)


@router.patch("/movies/{movie_id}/toggle", response_model=MovieResponse)
async def toggle_movie_status(
        movie_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Toggle movie active/inactive status (admin only).

    Enables or disables a movie without deleting it.
    Inactive movies won't appear in public endpoints.
    """
    movie = MovieService.toggle_movie_status(db=db, movie_id=movie_id)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    return MovieResponse.from_orm(movie)


# User Management
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=100),
        include_inactive: bool = Query(default=False, description="Include inactive users"),
        search: Optional[str] = Query(None, description="Search by email or name"),
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Get all users in the system (admin only).

    Allows administrators to view and manage user accounts.
    """
    query = db.query(User)

    if not include_inactive:
        query = query.filter(User.is_active == True)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            User.email.ilike(search_term) |
            User.first_name.ilike(search_term) |
            User.last_name.ilike(search_term)
        )

    users = query.offset(skip).limit(limit).all()

    return [UserResponse.from_orm(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_admin(
        user_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Get user details (admin only).

    Allows administrators to view detailed user information.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.from_orm(user)


@router.patch("/users/{user_id}/toggle", response_model=UserResponse)
async def toggle_user_status(
        user_id: int,
        db: Session = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    """
    Toggle user active/inactive status (admin only).

    Enables or disables user accounts.
    Inactive users cannot login or make purchases.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from disabling themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)
