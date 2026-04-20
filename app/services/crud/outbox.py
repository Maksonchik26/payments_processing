from app.db.models import  Outbox
from app.schemas.outbox import OutboxCreateIn
from app.services.crud.common import CRUD


class OutboxCRUD(CRUD):
    async def create(self, data: OutboxCreateIn) -> Outbox:
        outbox = Outbox(**data.model_dump(exclude_unset=True))
        self.session.add(outbox)

        return outbox

    async def update(self):
        pass

    async def delete(self):
        pass

    async def read_one(self):
        pass

    async def read_all(self):
        pass