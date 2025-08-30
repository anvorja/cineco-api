# app/api/v1/endpoints/purchases.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.services.purchase_service import PurchaseService
from app.services.email_service import EmailService
from app.schemas.purchase import PurchaseCreate, PurchaseResponse, PurchaseListResponse
from app.models import User

router = APIRouter()


@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
        purchase_data: PurchaseCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Create a new ticket purchase (authenticated users only).

    Process:
    1. Validates movie availability and ticket quantity
    2. Simulates payment processing (always successful in MVP)
    3. Creates purchase record and individual tickets
    4. Sends confirmation email

    Requires valid JWT token.
    """
    # Create purchase with tickets
    purchase = PurchaseService.create_purchase(
        db=db,
        user_id=current_user.id,
        purchase_data=purchase_data
    )

    # Send confirmation email (simulated)
    try:
        await EmailService.send_purchase_confirmation(
            user=current_user,
            purchase=purchase,
            tickets=purchase.tickets
        )
    except Exception as e:
        # Don't fail the purchase if email fails
        pass

    return PurchaseResponse.from_orm(purchase)


@router.get("/", response_model=List[PurchaseListResponse])
async def get_my_purchases(
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(default=10, ge=1, le=50, description="Maximum records to return"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Get purchase history for the authenticated user.

    Returns the user's purchase history with basic information.
    Use GET /purchases/{id} for detailed purchase information.
    """
    purchases = PurchaseService.get_user_purchases(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return [PurchaseListResponse.from_orm(purchase) for purchase in purchases]


@router.get("/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase_detail(
        purchase_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific purchase.

    Users can only view their own purchases.
    Returns complete purchase details including tickets and payment info.
    """
    purchase = PurchaseService.get_purchase_by_id(
        db=db,
        purchase_id=purchase_id,
        user_id=current_user.id  # Ensure user can only see their own purchases
    )

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found"
        )

    return PurchaseResponse.from_orm(purchase)
