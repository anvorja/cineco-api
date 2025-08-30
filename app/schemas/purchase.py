# app/schemas/purchases.py
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PaymentInfo(BaseModel):
    """Schema for payment information"""
    card_number: str = Field(..., pattern=r"^\d{16}$", description="16-digit card number")
    card_holder: str = Field(..., min_length=1, max_length=100, description="Cardholder name")
    expiry_month: int = Field(..., ge=1, le=12, description="Expiry month (1-12)")
    expiry_year: int = Field(..., ge=2024, description="Expiry year")
    cvv: str = Field(..., pattern=r"^\d{3,4}$", description="3 or 4 digit CVV")

    model_config = {
        "json_schema_extra": {
            "example": {
                "card_number": "1234567812345678",
                "card_holder": "Juan Perez",
                "expiry_month": 12,
                "expiry_year": 2025,
                "cvv": "123"
            }
        }
    }


class PurchaseCreate(BaseModel):
    """Schema for creating a purchase"""
    movie_id: int = Field(..., gt=0, description="Movie ID")
    quantity: int = Field(..., ge=1, le=10, description="Number of tickets (max 10)")
    payment_info: PaymentInfo = Field(..., description="Payment information")

    model_config = {
        "json_schema_extra": {
            "example": {
                "movie_id": 1,
                "quantity": 2,
                "payment_info": {
                    "card_number": "1234567812345678",
                    "card_holder": "Juan Perez",
                    "expiry_month": 12,
                    "expiry_year": 2025,
                    "cvv": "123"
                }
            }
        }
    }


class TicketResponse(BaseModel):
    """Schema for ticket response"""
    id: int
    ticket_code: str
    seat_number: str
    status: str
    created_at: datetime
    is_active: bool

    @classmethod
    def from_orm(cls, ticket):
        return cls(
            id=ticket.id,
            ticket_code=ticket.ticket_code,
            seat_number=ticket.seat_number,
            status=ticket.status.value,
            created_at=ticket.created_at,
            is_active=ticket.is_active
        )


class PurchaseResponse(BaseModel):
    """Schema for purchase response"""
    id: int
    user_id: int
    movie_id: int
    quantity: int
    total_amount: float
    status: str
    created_at: datetime
    is_confirmed: bool

    # Related data
    movie_title: str
    user_full_name: str
    tickets: List[TicketResponse]
    payment_summary: Dict[str, Any]

    @classmethod
    def from_orm(cls, purchase):
        return cls(
            id=purchase.id,
            user_id=purchase.user_id,
            movie_id=purchase.movie_id,
            quantity=purchase.quantity,
            total_amount=purchase.total_amount,
            status=purchase.status.value,
            created_at=purchase.created_at,
            is_confirmed=purchase.is_confirmed,
            movie_title=purchase.movie.title,
            user_full_name=purchase.user.full_name,
            tickets=[TicketResponse.from_orm(ticket) for ticket in purchase.tickets],
            payment_summary={
                "last_four": purchase.payment_info.get("last_four", "****") if purchase.payment_info else "****",
                "total_amount": purchase.total_amount,
                "currency": "COP"
            }
        )


class PurchaseListResponse(BaseModel):
    """Schema for purchase list response"""
    id: int
    movie_title: str
    quantity: int
    total_amount: float
    status: str
    created_at: datetime
    tickets_count: int

    @classmethod
    def from_orm(cls, purchase):
        return cls(
            id=purchase.id,
            movie_title=purchase.movie.title,
            quantity=purchase.quantity,
            total_amount=purchase.total_amount,
            status=purchase.status.value,
            created_at=purchase.created_at,
            tickets_count=len(purchase.tickets)
        )