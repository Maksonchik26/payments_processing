from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class OutboxCreateIn(BaseModel):
    topic: str = Field(..., max_length=255)
    payload: dict

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "topic": "Топик N",
                "payload": {
                    "additionalProp1": {}
                },
            }
        }
    }

