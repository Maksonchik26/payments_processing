from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.common.exceptions import (
    ResourceExists,
    NotFromTable,
    RequestCorrectNotFound,
    RedundantOperation,
    NotEnoughRights,
    ParameterCannotBeChanged,
)
from app.db.models import Payment, Outbox
from app.schemas.outbox import OutboxCreateIn
from app.schemas.payments import (
    PaymentCreateIn
)
from app.services.crud.outbox import OutboxCRUD
from app.services.crud.payments import PaymentsCRUD


class PaymentsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payments_crud = PaymentsCRUD(self.session)
        self.outbox_crud = OutboxCRUD(self.session)

    async def create_payment(self, idempotency_key: UUID, payment_data: PaymentCreateIn) -> Payment:
        payment_data.webhook_url = str(payment_data.webhook_url)
        async with self.session.begin():
            # Check existed payment
            existing = await self.payments_crud.read_by_idempotency_key(idempotency_key)
            if existing:
                return existing

            try:
                # Create new payment and outbox_event
                payment = await self.payments_crud.create(payment_data, idempotency_key)
                await self.session.flush()
                await self.outbox_crud.create(
                    OutboxCreateIn(
                        topic="payments.new",
                        payload={"payment_id": str(payment.payment_id)}
                    )
                )

            except IntegrityError as e:
                payment = await self.payments_crud.read_by_idempotency_key(idempotency_key)

        return payment


    async def get_payment(self, payment_id: UUID) -> Payment:
        payment = await self.payments_crud.read_one(payment_id)

        return payment
