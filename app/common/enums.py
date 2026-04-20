from enum import StrEnum


class OutboxStatusEnum(StrEnum):
    pending = "pending"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class PaymentStatusEnum(StrEnum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"

class CurrencyEnum(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
