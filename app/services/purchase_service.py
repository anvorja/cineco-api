# app/services/purchase_service.py
import random
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models import Purchase, Ticket, Movie, User, PurchaseStatus, TicketStatus
from app.schemas.purchase import PurchaseCreate, PaymentInfo
from app.utils.helpers import generate_ticket_code, mask_card_number


class PurchaseService:
    """Service for purchase operations"""

    @staticmethod
    def simulate_payment(payment_info: PaymentInfo) -> Dict[str, Any]:
        """
        Simulate payment processing (always successful for MVP).
        In production, this would integrate with a real payment gateway.

        Args:
            payment_info: Payment information

        Returns:
            Payment result dictionary
        """
        # Simulate processing time
        transaction_id = f"TXN-{random.randint(100000, 999999)}"

        # For MVP, payments always succeed
        return {
            "transaction_id": transaction_id,
            "status": "approved",
            "message": "Payment processed successfully (simulated)",
            "last_four": payment_info.card_number[-4:],
            "card_holder": payment_info.card_holder
        }

    @staticmethod
    def create_purchase(db: Session, user_id: int, purchase_data: PurchaseCreate) -> Purchase:
        """
        Create a new purchase with tickets.

        Args:
            db: Database session
            user_id: ID of the purchasing user
            purchase_data: Purchase creation data

        Returns:
            Created purchase object

        Raises:
            HTTPException: If movie not found, insufficient tickets, or payment fails
        """
        # Get movie and verify availability
        movie = db.query(Movie).filter(
            Movie.id == purchase_data.movie_id,
            Movie.is_active == True
        ).first()

        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found or not available"
            )

        # Check ticket availability
        if not movie.can_purchase(purchase_data.quantity):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {movie.available_tickets} tickets available"
            )

        # Calculate total amount
        total_amount = movie.price * purchase_data.quantity

        # Process payment (simulated)
        payment_result = PurchaseService.simulate_payment(purchase_data.payment_info)

        # Create purchase with atomic transaction
        try:
            # Reduce available tickets
            movie.available_tickets -= purchase_data.quantity

            # Create purchase record
            purchase = Purchase(
                user_id=user_id,
                movie_id=purchase_data.movie_id,
                quantity=purchase_data.quantity,
                total_amount=total_amount,
                status=PurchaseStatus.CONFIRMED,  # Immediately confirmed since payment succeeded
                payment_info={
                    "transaction_id": payment_result["transaction_id"],
                    "last_four": payment_result["last_four"],
                    "card_holder": payment_result["card_holder"],
                    "status": payment_result["status"]
                }
            )

            db.add(purchase)
            db.flush()  # Get purchase ID

            # Create individual tickets
            tickets = []
            for i in range(purchase_data.quantity):
                ticket_code = generate_ticket_code()
                # Ensure unique ticket code
                while db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first():
                    ticket_code = generate_ticket_code()

                ticket = Ticket(
                    purchase_id=purchase.id,
                    ticket_code=ticket_code,
                    seat_number=f"GENERAL-{i + 1}",
                    status=TicketStatus.ACTIVE
                )
                tickets.append(ticket)

            db.add_all(tickets)
            db.commit()
            db.refresh(purchase)

            return purchase

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing purchase"
            )

    @staticmethod
    def get_user_purchases(
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 10
    ) -> List[Purchase]:
        """
        Get purchases for a specific user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of purchase objects
        """
        return db.query(Purchase).filter(
            Purchase.user_id == user_id
        ).order_by(
            Purchase.created_at.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_purchase_by_id(db: Session, purchase_id: int, user_id: Optional[int] = None) -> Optional[Purchase]:
        """
        Get purchase by ID, optionally filtered by user.

        Args:
            db: Database session
            purchase_id: Purchase ID
            user_id: Optional user ID for authorization

        Returns:
            Purchase object if found, None otherwise
        """
        query = db.query(Purchase).filter(Purchase.id == purchase_id)

        if user_id:
            query = query.filter(Purchase.user_id == user_id)

        return query.first()

    @staticmethod
    def get_all_purchases(
            db: Session,
            skip: int = 0,
            limit: int = 20,
            movie_id: Optional[int] = None,
            user_id: Optional[int] = None,
            status: Optional[str] = None
    ) -> List[Purchase]:
        """
        Get all purchases with optional filters (admin only).

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            movie_id: Filter by movie ID
            user_id: Filter by user ID
            status: Filter by status

        Returns:
            List of purchase objects
        """
        query = db.query(Purchase)

        if movie_id:
            query = query.filter(Purchase.movie_id == movie_id)

        if user_id:
            query = query.filter(Purchase.user_id == user_id)

        if status:
            query = query.filter(Purchase.status == status.upper())

        return query.order_by(
            Purchase.created_at.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_sales_report(db: Session) -> Dict[str, Any]:
        """
        Generate sales report (admin only).

        Args:
            db: Database session

        Returns:
            Sales report dictionary
        """
        # Total sales
        total_purchases = db.query(Purchase).filter(
            Purchase.status == PurchaseStatus.CONFIRMED
        ).count()

        total_revenue = db.query(func.sum(Purchase.total_amount)).filter(
            Purchase.status == PurchaseStatus.CONFIRMED
        ).scalar() or 0

        total_tickets = db.query(func.sum(Purchase.quantity)).filter(
            Purchase.status == PurchaseStatus.CONFIRMED
        ).scalar() or 0

        # Average purchase amount
        avg_purchase = total_revenue / total_purchases if total_purchases > 0 else 0

        return {
            "total_purchases": total_purchases,
            "total_revenue": total_revenue,
            "total_tickets_sold": total_tickets,
            "average_purchase_amount": round(avg_purchase, 2),
            "currency": "COP"
        }
