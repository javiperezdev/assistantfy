from openai import AsyncOpenAI
from .whatsapp_service import send_message
import httpx

async def generate_response(phone_number : str, content: str, httpx_client: httpx.AsyncClient, ai_client: AsyncOpenAI):
    response =  await ai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant from a barbershop, your objective is to satisfy clients requests. Don't create texts that have more of 2 lines"},
            {"role": "user", "content": content},
        ],
        stream=False
    )

    clean_response = response.choices[0].message.content
    await send_message(phone_number, clean_response, httpx_client)
