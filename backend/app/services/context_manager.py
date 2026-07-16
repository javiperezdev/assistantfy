import json
import logging
from app.redis_client import redis_client

logger = logging.getLogger(__name__)

EXPIRATION_TIME = 86400

async def add_to_context(phone_number: str, message: dict):
    key = f"context:{phone_number}"
    await redis_client.rpush(key, json.dumps(message))
    await redis_client.expire(key, EXPIRATION_TIME)
    logger.debug("Context saved | phone=%s", phone_number)

async def get_context(phone_number: str):
    key = f"context:{phone_number}"
    text_data = await redis_client.lrange(key, 0, -1)
    if text_data:
        logger.debug("Context hit | phone=%s size=%d", phone_number, len(text_data))
        return [json.loads(item) for item in text_data]
    logger.debug("Context miss | phone=%s", phone_number)
    return []
