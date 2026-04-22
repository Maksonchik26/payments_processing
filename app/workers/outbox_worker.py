import asyncio
from datetime import datetime, timezone

from app.common.enums import OutboxStatusEnum
from app.config import settings
from app.db.models import Outbox
from app.infrastructure.common.retry import retry
from app.infrastructure.messaging.broker.broker import publish_event, broker
from app.infrastructure.outbox.repository import OutboxRepository
from app.db.base import async_session


async def worker_loop():
    await retry(
        action=broker.connect,
        name="Worker started",
    )

    try:
        while True:
            event_ids = []
            async with async_session() as session:
                async with session.begin():
                    repo = OutboxRepository(session)

                    events = await repo.fetch_pending()

                    if not events:
                        events = []

                    for event in events:
                        event.status = OutboxStatusEnum.processing.value
                        event_ids.append(event.outbox_id)

            if not event_ids:
                await asyncio.sleep(settings.POLL_INTERVAL)


            for event_id in event_ids:
                # Try publish to broker
                try:
                    async with async_session() as session:
                        async with session.begin():
                            event_db = await session.get(Outbox, event_id)

                            if event_db.status != OutboxStatusEnum.processing.value:
                                continue

                    await publish_event(event_db.topic, event_db.payload)

                except Exception as e:
                    #  ERROR handling
                    async with async_session() as session:
                        async with session.begin():
                            event_db = await session.get(Outbox, event_id)

                            event_db.retry_count += 1
                            event_db.last_error = str(e)

                            to_dlq = False

                            if event_db.retry_count >= 3:
                                event_db.status = OutboxStatusEnum.failed.value
                                event_db.topic = "payments.dlq"
                                to_dlq = True
                            else:
                                event_db.status = OutboxStatusEnum.pending.value

                    # Publish to DLQ
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
                        event_db.processed_at = datetime.now(timezone.utc)
                        await asyncio.sleep(0.2)

    finally:
        await broker.close()


if __name__ == "__main__":
    asyncio.run(worker_loop())
