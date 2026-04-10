# app/api/v1/endpoints/purchases.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.purchase_service import PurchaseService
from app.services.email_service import EmailService
from app.schemas.purchase import PurchaseCreate, PurchaseResponse, PurchaseListResponse
from app.models import User

router = APIRouter()


@router.post("", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
        purchase_data: PurchaseCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Crear una nueva compra de boletos (solo usuarios autenticados).

    Proceso:
    1. Valida la disponibilidad de la película y la cantidad de boletos
    2. Simula el procesamiento de pago (siempre exitoso en el MVP)
    3. Crea el registro de la compra y los boletos individuales
    4. Envía correo de confirmación

    Requiere un token JWT válido.
    """
    # Create purchase with tickets
    purchase = PurchaseService.create_purchase(
        db=db,
        user_id=current_user.id,
        purchase_data=purchase_data
    )

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


@router.get("", response_model=List[PurchaseListResponse])
async def get_my_purchases(
        skip: int = Query(default=0, ge=0, description="Número de registros a omitir"),
        limit: int = Query(default=10, ge=1, le=50, description="Número máximo de registros a devolver"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtener el historial de compras del usuario autenticado.

    Retorna el historial de compras del usuario con información básica.
    Usa GET /purchases/{id} para obtener información detallada de una compra.
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
    Obtener información detallada de una compra específica.

    Los usuarios solo pueden ver sus propias compras.
    Retorna los detalles completos de la compra incluyendo boletos e información de pago.
    """
    purchase = PurchaseService.get_purchase_by_id(
        db=db,
        purchase_id=purchase_id,
        user_id=current_user.id
    )

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra no encontrada"
        )

    return PurchaseResponse.from_orm(purchase)
