from uuid import UUID

from fastapi import APIRouter, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_async_session
from app.schemas.payments import (
    PaymentCreateIn,
    PaymentCreateOut,
    PaymentSearchOut,
)
from app.services.operations.payments import PaymentsService

router = APIRouter(
    tags=['payments']
)


@router.post("/payments", status_code=status.HTTP_202_ACCEPTED, response_model=PaymentCreateOut)
async def create_payment(
    payment_data: PaymentCreateIn,
    session: AsyncSession = Depends(get_async_session),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    payment_service = PaymentsService(session)
    payment = await payment_service.create_payment(idempotency_key, payment_data)

    return payment


@router.get("/payments/{payment_id}", status_code=status.HTTP_200_OK, response_model=PaymentSearchOut | None)
async def create_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    payment_service = PaymentsService(session)
    payment = await payment_service.get_payment(payment_id)

    return payment
