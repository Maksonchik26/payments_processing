from pydantic import BaseModel
from uuid import UUID


class PaymentCreatedEvent(BaseModel):
    payment_id: UUID