# app/api/v1/endpoints/movies.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.movie_service import MovieService
from app.schemas.movie import MovieResponse, MovieListResponse

router = APIRouter()


@router.get("/", response_model=List[MovieListResponse])
async def get_movies(
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(default=10, ge=1, le=50, description="Maximum records to return"),
        db: Session = Depends(get_db)
):
    """
    Get all available movies (public endpoint).

    Returns list of active movies with available tickets.
    Anyone can access this endpoint without authentication.
    """
    movies = MovieService.get_movies(
        db=db,
        skip=skip,
        limit=limit,
        include_inactive=False,
        available_only=True
    )

    return [MovieListResponse.from_orm(movie) for movie in movies]


@router.get("/search", response_model=List[MovieListResponse])
async def search_movies(
        q: Optional[str] = Query(None, description="Search in title and description"),
        genre: Optional[str] = Query(None, description="Filter by genre"),
        min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
        max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
        rating: Optional[str] = Query(None, pattern="^(G|PG|PG-13|R|NC-17)$", description="Movie rating"),
        available_only: bool = Query(True, description="Only movies with available tickets"),
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(default=10, ge=1, le=50, description="Maximum records to return"),
        db: Session = Depends(get_db)
):
    """
    Search and filter movies (public endpoint).

    - **q**: Search term for title and description
    - **genre**: Filter by movie genre
    - **min_price**: Minimum ticket price
    - **max_price**: Maximum ticket price
    - **rating**: Movie rating (G, PG, PG-13, R, NC-17)
    - **available_only**: Show only movies with available tickets

    Anyone can use this endpoint to find movies with filters.
    """
    movies = MovieService.get_movies(
        db=db,
        skip=skip,
        limit=limit,
        include_inactive=False,
        search=q,
        genre=genre,
        min_price=min_price,
        max_price=max_price,
        rating=rating,
        available_only=available_only
    )

    return [MovieListResponse.from_orm(movie) for movie in movies]


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
        movie_id: int,
        db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific movie (public endpoint).

    Returns detailed movie information including availability.
    Anyone can access this endpoint to see movie details.
    """
    movie = MovieService.get_movie_by_id(db=db, movie_id=movie_id, include_inactive=False)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    return MovieResponse.from_orm(movie)


@router.get("/{movie_id}/availability", response_model=dict)
async def get_movie_availability(
        movie_id: int,
        db: Session = Depends(get_db)
):
    """
    Get movie ticket availability information (public endpoint).

    Returns availability details for ticket purchasing decisions.
    Anyone can check ticket availability before registering.
    """
    movie = MovieService.get_movie_by_id(db=db, movie_id=movie_id, include_inactive=False)

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )

    return {
        "movie_id": movie.id,
        "title": movie.title,
        "price": movie.price,
        "max_capacity": movie.max_capacity,
        "available_tickets": movie.available_tickets,
        "sold_tickets": movie.sold_tickets,
        "is_available": movie.is_available,
        "occupancy_rate": movie.occupancy_rate
    }
