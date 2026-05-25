import json
from openai import AsyncOpenAI
from sqlmodel import Session
from .whatsapp_service import send_message
from datetime import datetime
from zoneinfo import ZoneInfo
from .business_service import get_business_by_id
from .service_service import get_services_catalog
from app.schemas.ai_tools import get_all_tool_definitions
from app.schemas.schemas_whatsapp import WhatsappContext
from .tool_handler import execute_tool
from .context_manager import save_context
import httpx

async def generate_system_prompt(session, business_id: int):
    """
    Method in charge of generate the system prompt during runtime, this method is triggered by 
    routers/whatsapp send_messagge method, which gives AI the business logic for each different 
    request. As context, it gets business related info and the current time depending of the business tz.
    """

    # Business info from the database
    business = await get_business_by_id(session, business_id)
    tz = ZoneInfo(business.timezone)
    current_time = datetime.now(tz)
    
    day_of_week = current_time.strftime("%A") 
    current_date = current_time.strftime("%Y-%m-%d")
    current_hour = current_time.strftime("%H:%M")

    # Provisional prompt
    prompt = f"""
    Eres el asistente virtual oficial de '{business.name}'. 
    Tu único objetivo es ayudar a los clientes a reservar citas de forma eficiente, amable y conversacional.

    <contexto_temporal>
    - Hoy es {day_of_week}, {current_date}.
    - La hora actual es {current_hour}. 
    Utiliza esta información para calcular correctamente fechas relativas (ej. "mañana", "el próximo martes").
    </contexto_temporal>

    <catalogo_servicios>
    Estos son los únicos servicios que ofrecemos:
    {await get_services_catalog(business_id, session)}
    </catalogo_servicios>

    ### FLUJO DE CONVERSACIÓN OBLIGATORIO
    Sigue estos pasos en orden estricto:
    1. **Asignación Automática:** Si el cliente pide algo que encaja con un servicio, ASÚMELO AUTOMÁTICAMENTE. Pasa al paso 2.
    2. **Fecha y Hora:** Si ya sabes el servicio y el día, pregúntale a qué hora le viene bien.
    3. **Disponibilidad:** Usa `get_available_slots` para buscar huecos. 
    4. **Ofrecer Opciones:** Si hay huecos, ofrece un MÁXIMO de 3 opciones.
    5. **Pedir el Nombre:** Cuando el cliente confirme la hora exacta (ej. "a las 17:30"), DEBES preguntarle su nombre ANTES de hacer la reserva. (Ej: "¡Genial! ¿Me dices tu nombre para dejarlo reservado?").
    6. **Confirmar Reserva:** Usa `book_appointment` cuando tengas hora y nombre. **Usa siempre worker_id=1** por defecto (a menos que el cliente pida a alguien en específico). NO vuelvas a comprobar la disponibilidad, reserva directamente.

    ### REGLAS ESTRICTAS (¡CRÍTICO!)
    - **SILENCIO AL USAR HERRAMIENTAS:** Cuando decidas llamar a una función (`get_available_slots` o `book_appointment`), NO GENERES NINGÚN TEXTO (`content`). Llama a la función directamente sin justificarte ni hablar contigo mismo.
    - **CERO DOBLES CONFIRMACIONES:** Si el cliente ya aceptó una hora, no le preguntes "¿te parece bien?", pídele el nombre o reserva de inmediato.
    - **NO INVENTES DATOS:** Nunca inventes el nombre del cliente. Si no te lo ha dado explícitamente en esta conversación, pídeselo.
    - Eres un humano chateando por WhatsApp, NUNCA menciones términos como "ID", "base de datos", "herramienta" o "trabajador".
    """
    
    return prompt

async def generate_response(
    client_phone_number: str, 
    context: list, 
    httpx_client: httpx.AsyncClient, 
    ai_client: AsyncOpenAI, 
    system_prompt: str, 
    business_id: int,
    session: Session
):


    business_context = WhatsappContext(
        client_phone_number=client_phone_number,
        business_id=business_id
    )

    # Context for the ReAct loop -> (Reason -> Act)
    conversation = [ 
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)}
    ]
    
    max_turns = 5
    current_turns = 0

    while max_turns > current_turns:
        current_turns += 1
        
        response = await ai_client.chat.completions.create(
            model="deepseek-chat",
            messages=conversation,
            stream=False,
            tools=get_all_tool_definitions(),
            temperature=0.1
        )

        message = response.choices[0].message
        print(message)

        if not message.tool_calls:
            context.append({"role": "assistant", "content": message.content})
            await save_context(client_phone_number, context)
            await send_message(client_phone_number, message.content, httpx_client)
            return 

        message_dict = message.model_dump(exclude_none=True)

        # Removes the message AI generates when calling a tool (example: Client asked x so I am going to use y)

        if "content" in message_dict:
            message_dict["content"] = None

        conversation.append(message_dict)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            result = await execute_tool(name, args, business_context, session)
            print(f"tool result: {result}")
            
            # To gather all the context of the reasoning
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })
            
    error_message = "Lo siento, ha ocurrido un problema procesando tu solicitud. ¿Podemos intentarlo de nuevo?"
    await send_message(client_phone_number, error_message, httpx_client)
