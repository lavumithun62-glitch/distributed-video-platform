import redis.asyncio as redis

from backend.shared.config import settings


redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def check_redis():
    return await redis_client.ping()


async def close_redis():
    await redis_client.aclose()