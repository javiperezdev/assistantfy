import json
from openai import AsyncOpenAI
from sqlmodel import Session
from .whatsapp_service import send_message
from datetime import datetime
from zoneinfo import ZoneInfo
from .business_service import get_business_by_id
from .service_service import get_services_catalog
from app.schemas.ai_tools import tools
from app.schemas.schemas_whatsapp import WhatsappContext
from .tool_handler import execute_tool
import httpx

async def generate_system_prompt(session, business_id: int):
    # Business info from the database
    business = await get_business_by_id(session, business_id)
    tz = ZoneInfo(business.timezone)
    current_time = datetime.now(tz)
    
    day_of_week = current_time.strftime("%A") 
    current_date = current_time.strftime("%Y-%m-%d")
    current_hour = current_time.strftime("%H:%M")

    # Provisional prompt
    prompt =  f"""
    Eres el asistente virtual oficial de '{business.name}'. 
    Tu único objetivo es ayudar a los clientes a reservar citas de forma eficiente y amable.

    --- CONTEXTO TEMPORAL ---
    - Hoy es {day_of_week}, {current_date}.
    - La hora actual es {current_hour}. 
    Usa esto para calcular correctamente fechas relativas como "hoy", "mañana" o "el próximo martes".

    --- CATÁLOGO DE SERVICIOS ---
    Estos son los únicos servicios que ofrecemos. Cuando uses la herramienta 'get_available_slots_for_ai', DEBES usar el ID exacto que aparece aquí:
    {await get_services_catalog(business_id, session)}

    --- FLUJO DE CONVERSACIÓN OBLIGATORIO ---
    1. Si no sabes qué servicio quiere el cliente, PREGÚNTALE antes de buscar huecos.
    2. Si el cliente no especifica fecha, pregúntale para cuándo lo quiere.
    3. Si la herramienta devuelve horas libres, ofrécele un MÁXIMO de 3 opciones espaciadas para no agobiarle por WhatsApp.
    4. Si la herramienta devuelve una lista vacía, dile que ese día está completo y ofrécele mirar en el día siguiente.

    --- REGLAS ESTRICTAS ---
    - NUNCA inventes horarios ni asumas que hay hueco sin usar la herramienta.
    - RESPUESTAS CORTAS: Estás en WhatsApp, no escribas párrafos largos. Usa listas de puntos si es necesario.
    - No ofrezcas servicios que no estén en el catálogo. Si preguntan por otra cosa, diles educadamente que no lo hacéis.
    - Mantén un tono profesional, cercano y usa 1 o 2 emojis como máximo por mensaje.
    """
    
    return prompt

async def generate_response(
    client_phone_number: str, 
    content: str, 
    httpx_client: httpx.AsyncClient, 
    ai_client: AsyncOpenAI, 
    system_prompt: str, 
    business_id: int,
    session: Session
):

    context = WhatsappContext(
        client_phone_number=client_phone_number,
        negocio_id=business_id
    )

    # Currently after new message, ai loses context (Implementing redis could be a good choice)
    conversation = [ 
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    
    max_turns = 5
    current_turns = 0

    while max_turns > current_turns:
        current_turns += 1
        
        response = await ai_client.chat.completions.create(
            model="deepseek-chat",
            messages=conversation,
            stream=False,
            tools=tools,
            temperature=0.1
        )

        message = response.choices[0].message
        print(message)
        conversation.append(message)
        print(message.content)

        if not message.tool_calls:
            print("ha entrado aqui")
            await send_message(client_phone_number, message.content, httpx_client)
            return 

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            result = await execute_tool(name, args, context, session)
            
            # To gather all the context of the reasoning
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })
            
    error_message = "Lo siento, ha ocurrido un problema procesando tu solicitud. ¿Podemos intentarlo de nuevo?"
    await send_message(client_phone_number, error_message, httpx_client)
