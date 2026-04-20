from sqlalchemy import select

from app.common.enums import OutboxStatusEnum
from app.db.models import Outbox


class OutboxRepository:
    def __init__(self, session):
        self.session = session

    async def fetch_pending(self, limit: int = 100) -> list[Outbox]:
        result = await self.session.execute(
            select(Outbox)
            .where(Outbox.status == "pending")
            .limit(limit)
        )

        return result.scalars().all()
