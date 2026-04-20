from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange
from app.config import settings

broker = RabbitBroker(
    f"amqp://{settings.BROKER_USER}:{settings.BROKER_PASSWORD}@{settings.BROKER_HOST}:{settings.BROKER_PORT}/"
)


async def publish_event(topic: str, payload: dict):
    await broker.publish(
        message=payload,
        routing_key=topic,
    )

