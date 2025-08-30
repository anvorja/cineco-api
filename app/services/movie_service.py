# app/services/movie_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from fastapi import HTTPException, status

from app.models import Movie
from app.schemas.movie import MovieCreate, MovieUpdate


class MovieService:
    """Service for movie operations"""

    @staticmethod
    def create_movie(db: Session, movie_data: MovieCreate) -> Movie:
        """
        Create a new movie (admin only).

        Args:
            db: Database session
            movie_data: Movie creation data

        Returns:
            Created movie object
        """
        # Check if movie title already exists (case insensitive)
        existing_movie = db.query(Movie).filter(
            Movie.title.ilike(movie_data.title.strip())
        ).first()

        if existing_movie:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Movie with title '{movie_data.title}' already exists"
            )

        movie = Movie(
            title=movie_data.title.strip(),
            description=movie_data.description.strip(),
            genre=movie_data.genre.strip(),
            duration=movie_data.duration,
            rating=movie_data.rating.upper(),
            price=movie_data.price,
            max_capacity=movie_data.max_capacity,
            available_tickets=movie_data.available_tickets,
            image_url=movie_data.image_url.strip() if movie_data.image_url else None
        )

        db.add(movie)
        db.commit()
        db.refresh(movie)

        return movie

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int, include_inactive: bool = False) -> Optional[Movie]:
        """
        Get movie by ID.

        Args:
            db: Database session
            movie_id: Movie ID
            include_inactive: Include inactive movies

        Returns:
            Movie object if found, None otherwise
        """
        query = db.query(Movie).filter(Movie.id == movie_id)

        if not include_inactive:
            query = query.filter(Movie.is_active == True)

        return query.first()

    @staticmethod
    def get_movies(
            db: Session,
            skip: int = 0,
            limit: int = 10,
            include_inactive: bool = False,
            search: Optional[str] = None,
            genre: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            rating: Optional[str] = None,
            available_only: bool = True
    ) -> List[Movie]:
        """
        Get movies with filters.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            include_inactive: Include inactive movies
            search: Search term for title/description
            genre: Filter by genre
            min_price: Minimum price filter
            max_price: Maximum price filter
            rating: Filter by rating
            available_only: Only movies with available tickets

        Returns:
            List of movie objects
        """
        query = db.query(Movie)

        # Active filter
        if not include_inactive:
            query = query.filter(Movie.is_active == True)

        # Search filter
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Movie.title.ilike(search_term),
                    Movie.description.ilike(search_term)
                )
            )

        # Genre filter
        if genre:
            query = query.filter(Movie.genre.ilike(f"%{genre.strip()}%"))

        # Price filters
        if min_price is not None:
            query = query.filter(Movie.price >= min_price)
        if max_price is not None:
            query = query.filter(Movie.price <= max_price)

        # Rating filter
        if rating:
            query = query.filter(Movie.rating == rating.upper())

        # Available tickets filter
        if available_only:
            query = query.filter(Movie.available_tickets > 0)

        # Order by created date (newest first)
        query = query.order_by(desc(Movie.created_at))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_movie(db: Session, movie_id: int, movie_data: MovieUpdate) -> Optional[Movie]:
        """
        Update movie (admin only).

        Args:
            db: Database session
            movie_id: Movie ID to update
            movie_data: Updated movie data

        Returns:
            Updated movie object or None if not found
        """
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return None

        # Update only provided fields
        update_data = movie_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(movie, field):
                if isinstance(value, str):
                    value = value.strip()
                if field == "rating" and value:
                    value = value.upper()
                setattr(movie, field, value)

        db.commit()
        db.refresh(movie)

        return movie

    @staticmethod
    def toggle_movie_status(db: Session, movie_id: int) -> Optional[Movie]:
        """
        Toggle movie active status (admin only).

        Args:
            db: Database session
            movie_id: Movie ID

        Returns:
            Updated movie object or None if not found
        """
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return None

        movie.is_active = not movie.is_active
        db.commit()
        db.refresh(movie)

        return movie

    @staticmethod
    def delete_movie(db: Session, movie_id: int) -> bool:
        """
        Soft delete movie by setting is_active to False.

        Args:
            db: Database session
            movie_id: Movie ID

        Returns:
            True if deleted, False if not found
        """
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return False

        movie.is_active = False
        db.commit()

        return True
