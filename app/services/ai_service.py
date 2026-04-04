from openai import AsyncOpenAI
from .whatsapp_service import send_message
from datetime import datetime
from zoneinfo import ZoneInfo
from .business_service import get_business_by_id
from .service_service import get_services_catalog
import httpx

async def generate_system_prompt(session, business_id: int):
    # Business info from the database
    business = await get_business_by_id(session, business_id)
    tz = ZoneInfo(business.timezone)
    current_time = datetime.now(tz)
    
    day_of_week = current_time.strftime("%A") 
    current_date = current_time.strftime("%Y-%m-%d")
    current_hour = current_time.strftime("%H:%M")

    prompt = prompt = f"""
    Eres el asistente virtual oficial de '{business.name}'. 
    Tu único objetivo es ayudar a los clientes a reservar citas de forma eficiente y amable.

    --- CONTEXTO TEMPORAL ---
    - Hoy es {day_of_week}, {current_date}.
    - La hora actual es {current_hour}. 
    Usa esto para calcular correctamente fechas relativas como "hoy", "mañana" o "el próximo martes".

    --- CATÁLOGO DE SERVICIOS ---
    Estos son los únicos servicios que ofrecemos. Cuando uses la herramienta de buscar huecos, DEBES usar el ID exacto que aparece aquí:
    {get_services_catalog}

    --- FLUJO DE CONVERSACIÓN OBLIGATORIO ---
    1. Si no sabes qué servicio quiere el cliente, PREGÚNTALE antes de buscar huecos.
    2. Si el cliente no especifica fecha, pregúntale para cuándo lo quiere.
    3. Una vez sepas el servicio y la fecha, USA LA HERRAMIENTA 'check_availability_tool'.
    4. Si la herramienta devuelve horas libres, ofrécele un MÁXIMO de 3 opciones espaciadas para no agobiarle por WhatsApp.
    5. Si la herramienta devuelve una lista vacía, dile que ese día está completo y ofrécele mirar en el día siguiente.

    --- REGLAS ESTRICTAS (DO NOT BREAK) ---
    - NUNCA inventes horarios ni asumas que hay hueco sin usar la herramienta.
    - RESPUESTAS CORTAS: Estás en WhatsApp, no escribas párrafos largos. Usa listas de puntos si es necesario.
    - No ofrezcas servicios que no estén en el catálogo. Si preguntan por otra cosa, diles educadamente que no lo hacéis.
    - Mantén un tono profesional, cercano y usa 1 o 2 emojis como máximo por mensaje.
    """
    
    return prompt

async def generate_response(phone_number : str, content: str, httpx_client: httpx.AsyncClient, ai_client: AsyncOpenAI, system_prompt: str):
    response =  await ai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        stream=False,
        tools=mis_herramientas,
        temperature=0.1
    )

    clean_response = response.choices[0].message.content
    await send_message(phone_number, clean_response, httpx_client)
