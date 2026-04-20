from uuid import UUID

from sqlalchemy import select, and_

from app.db.models import Payment
from app.schemas.payments import PaymentCreateDB
from app.services.crud.common import CRUD


class PaymentsCRUD(CRUD):
    async def read_all (self, limit: int = 10, offset: int = 0) -> list[Payment]:
        commission_definitions = await self.session.execute(select(Payment).limit(limit).offset(offset))
        result = commission_definitions.scalars().all()

        return result

    async def read_one(self, payment_id: UUID) -> Payment:
        payment = await self.session.execute(
            select(Payment).filter(Payment.payment_id == payment_id)
        )
        result = payment.scalars().first()

        return result

    async def read_by_idempotency_key(self, idempotency_key: UUID) -> Payment:
        payment = await self.session.execute(
            select(Payment).filter(Payment.idempotency_key == idempotency_key)
        )
        result = payment.scalars().first()

        return result

    async def create(self, data: PaymentCreateDB, idempotency_key: str) -> Payment:
        payment = Payment(**data.model_dump(exclude_unset=True), idempotency_key=idempotency_key)
        self.session.add(payment)

        return payment

    async def update(self):
        pass

    async def delete(self):
        pass