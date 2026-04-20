from faststream.rabbit import RabbitBroker, RabbitQueue
from faststream.rabbit.fastapi import RabbitRouter

from app.config import settings

router = RabbitRouter



broker = RabbitBroker(
    f"amqp://{settings.BROKER_USER}:{settings.BROKER_PASSWORD}@{settings.BROKER_HOST}:{settings.BROKER_PORT}/"
)

queue = RabbitQueue("payments.queue")


@broker.subscriber(queue)
async def dummy(msg: dict):
    print(msg)

async def publish_payment_event():
    await broker.publish(
        message={
            "payment_id": 123,
            "status": "created",
            "amount": 1000,
        },
        queue="payments.queue",  # можно routing_key тоже
    )

if __name__ == "__main__":
    import asyncio

    async def main():
        await broker.connect()
        await publish_payment_event()

    asyncio.run(main())