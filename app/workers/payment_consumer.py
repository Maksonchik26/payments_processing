import random
import asyncio
import logging
import sys
from datetime import datetime, timezone

from app.db.base import async_session
from app.db.models import Payment
from app.infrastructure.common.retry import retry
from app.infrastructure.http.webhook_client import send_webhook
from app.infrastructure.messaging.broker.broker import broker, start_consume_with_retry


async def send_webhook_with_retry(url: str, payload: dict, retries: int = 3) -> None:
    for attempt in range(retries):
        try:
            await send_webhook(url, payload)
            return
        except Exception as e:
            logging.warning(
                f"Webhook failed attempt {attempt + 1}/{retries}: {e}"
            )

            if attempt == retries - 1:
                continue

            await asyncio.sleep(2 ** attempt)

    logging.error(
        "Webhook delivery failed after retries",
        extra=payload
    )


@broker.subscriber("payments.new")
async def handle_payment(event: dict):
    async with async_session()  as session:
        async with session.begin():
            payment = await session.get(Payment, event["payment_id"])

            if not payment:
                return

            if payment.status != "pending":
                return

            await asyncio.sleep(random.randint(2, 5))

            success = random.random() < 0.9

            payment.status = "succeeded" if success else "failed"
            payment.processed_at = datetime.now(timezone.utc)

    await send_webhook_with_retry(
        payment.webhook_url,
        {
            "payment_id": str(payment.payment_id),
            "status": payment.status,
        }
    )


@broker.subscriber("payments.dlq")
async def handle_dlq(event: dict):
    print("DLQ message:", event)

async def main() -> None:
    async with broker:
        await retry(
            action=broker.start,
            name="Consumer started",
        )
        await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
