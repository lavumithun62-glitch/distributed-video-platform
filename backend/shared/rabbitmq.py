import aio_pika

from backend.shared.config import settings


async def get_rabbitmq_connection():
    return await aio_pika.connect_robust(
        settings.rabbitmq_url
    )


async def publish_message(queue_name: str, message: dict):
    import json

    connection = await get_rabbitmq_connection()

    try:
        channel = await connection.channel()

        queue = await channel.declare_queue(
            queue_name,
            durable=True,
        )

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
            ),
            routing_key=queue.name,
        )

    finally:
        await connection.close()