import json
from app.redis_client import redis_client

EXPIRATION_TIME = 86400

async def add_to_context(phone_number: str, message: dict):
    key = f"context:{phone_number}"
    await redis_client.rpush(key, json.dumps(message))
    await redis_client.expire(key, EXPIRATION_TIME)

async def get_context(phone_number: str):
    key = f"context:{phone_number}"
    text_data = await redis_client.lrange(key, 0, -1)
    if text_data:
        return [json.loads(item) for item in text_data]
    return []
