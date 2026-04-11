import json
from app.redis_client import redis_client

EXPIRATION_TIME = 86400

async def save_context(phone_number: str, data: dict):
    key = f"context:{phone_number}"
    text_data = json.dumps(data)
    await redis_client.set(key, text_data, ex=EXPIRATION_TIME)

async def get_context(phone_number: str):
    key = f"context:{phone_number}"
    
    text_data = await redis_client.get(key)
    
    if text_data:
        return json.loads(text_data)

    return []

async def delete_context(phone_number: str):
    await redis_client.delete(f"context:{phone_number}")