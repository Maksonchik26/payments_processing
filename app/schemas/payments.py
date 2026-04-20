from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.common.enums import CurrencyEnum, PaymentStatusEnum


class PaymentCreateIn(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: CurrencyEnum
    description: str | None = Field(None, max_length=255)
    metadata_json: dict | None = Field(None)
    webhook_url: HttpUrl


    model_config = {
        "extra": "forbid",
        "use_enum_values": True,

        "json_schema_extra": {
            "example": {
                "amount": "325026.32",
                "currency": "RUB",
                "description": "Платеж определенного банка",
                "metadata": {"key": "val"},
                "webhook_url": "http://url.ru"
            }
        }
    }


class PaymentCreateDB(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: CurrencyEnum
    description: str | None = Field(None, max_length=255)
    metadata: dict | None = None
    webhook_url: str


class PaymentCreateOut(BaseModel):
    payment_id: UUID
    status: str
    created_at: datetime


class PaymentSearchOut(BaseModel):
    payment_id: UUID
    amount: Decimal
    currency: CurrencyEnum
    description: str | None
    metadata_json: dict | None
    status: PaymentStatusEnum
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None
