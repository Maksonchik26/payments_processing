from faststream.rabbit import RabbitBroker
from app.config import settings

broker = RabbitBroker(settings.BROKER_URL)


async def publish_event(topic: str, payload: dict):
    await broker.publish(
        message=payload,
        routing_key=topic,
    )
