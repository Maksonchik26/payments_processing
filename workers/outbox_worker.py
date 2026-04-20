import asyncio

from app.common.enums import OutboxStatusEnum
from app.db.models import Outbox
from app.infrastructure.messaging.broker.broker import publish_event, broker
from app.infrastructure.outbox.repository import OutboxRepository
from app.db.base import async_session


async def worker_loop():
    await broker.connect()

    try:
        while True:
            event_ids = []
            async with async_session() as session:
                async with session.begin():
                    repo = OutboxRepository(session)

                    events = await repo.fetch_pending()

                    if not events:
                        await asyncio.sleep(1)
                        continue

                    for event in events:
                        event.status = OutboxStatusEnum.processing.value
                        event_ids.append(event.outbox_id)

            for event_id in event_ids:
                try:
                    async with async_session() as session:
                        async with session.begin():
                            event_db = await session.get(Outbox, event_id)

                            if event_db.status != OutboxStatusEnum.processing.value:
                                continue

                            payload = event_db.payload
                            topic = event_db.topic

                    await publish_event(topic, payload)

                except Exception as e:
                    #  ERROR handling (NEW TX)
                    async with async_session() as session:
                        async with session.begin():
                            event_db = await session.get(Outbox, event_id)

                            event_db.retry_count += 1
                            event_db.last_error = str(e)

                            to_dlq = False

                            if event_db.retry_count >= 3:
                                event_db.status = OutboxStatusEnum.failed.value
                                to_dlq = True
                            else:
                                event_db.status = OutboxStatusEnum.pending.value

                    if to_dlq:
                        await publish_event("payments.dlq", event_db.payload)

                    continue

                # SUCCESS finalize (NEW TX)
                async with async_session() as session:
                    async with session.begin():
                        event_db = await session.get(Outbox, event_id)

                        if event_db.status != OutboxStatusEnum.processing.value:
                            continue

                        event_db.status = OutboxStatusEnum.processed.value
            await asyncio.sleep(0.2)

    finally:
        await broker.close()


if __name__ == "__main__":
    asyncio.run(worker_loop())
