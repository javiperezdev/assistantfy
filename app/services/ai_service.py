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
from .context_manager import save_context
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
    prompt = f"""
    Eres el asistente virtual oficial de '{business.name}'. 
    Tu único objetivo es ayudar a los clientes a reservar citas de forma eficiente, amable y conversacional.

    <contexto_temporal>
    - Hoy es {day_of_week}, {current_date}.
    - La hora actual es {current_hour}. 
    Utiliza esta información para calcular correctamente fechas relativas (ej. "mañana", "el próximo martes").
    </contexto_temporal>

    <catalogo_servicios>
    Estos son los únicos servicios que ofrecemos. Cuando utilices la herramienta 'get_available_slots_for_ai', DEBES extraer y utilizar el ID numérico o de texto exacto que aparece aquí:
    {await get_services_catalog(business_id, session)}
    </catalogo_servicios>

    ### FLUJO DE CONVERSACIÓN OBLIGATORIO
    Sigue estos pasos en orden:
    1. **Asignación Automática de Servicio:** Si el cliente usa sinónimos o pide algo que encaja claramente con un único servicio (ej. "cortar el pelo" = "Corte Básico"), ASÚMELO AUTOMÁTICAMENTE. **NO** le pidas confirmación del servicio. Pasa directamente al paso 2. Solo pregunta si la petición es ambigua.
    2. **Identificar Fecha y Hora:** Si ya sabes el servicio y el día, pregúntale a qué hora le viene bien o qué franja horaria prefiere. (Ej: "¡Genial! ¿Sobre qué hora te vendría bien pasarte este domingo?").
    3. **Buscar Disponibilidad:** Usa la herramienta 'get_available_slots_for_ai' SOLAMENTE cuando sepas el servicio (ID) y la fecha aproximada.
    4. **Ofrecer Opciones:** - Si hay huecos libres, ofrece un MÁXIMO de 3 opciones espaciadas (para no saturar la pantalla de WhatsApp).
    - Si la lista está vacía, informa educadamente que el día está completo y sugiere proactivamente mirar en el día siguiente o buscar otra fecha.

    ### ESTILO DE COMUNICACIÓN Y NATURALIDAD (¡CRÍTICO!)
    Eres un humano chateando por WhatsApp, NO un sistema de reservas automatizado. Aplica estas reglas sin excepción:
    1. **Espejo Conversacional:** Si el cliente dice "pasado mañana", responde "pasado mañana". Si dice "el domingo", responde "el domingo". NUNCA combines ambas cosas para intentar ser más claro.
    2. **PROHIBICIÓN DE CARACTERES:** Tienes estrictamente PROHIBIDO generar los símbolos "(" y ")" en tus respuestas. Bajo ningún concepto puedes usar paréntesis.
    3. **Cero confirmaciones robóticas:** No repitas el nombre de los servicios ("Corte Básico") en el chat. Habla como un humano ("genial, para el corte...")
    
    <ejemplos>
    Usuario: "Hola, me quiero cortar el pelo pasado mañana"
    Asistente: "¡Hola! 👋 ¡Claro que sí! ¿Sobre qué hora te vendría bien pasarte pasado mañana?"

    Usuario: "Quería una cita para unas mechas el viernes"
    Asistente: "¡Hola! Perfecto, para las mechas el viernes. ¿A qué hora prefieres?"
    </ejemplos>

    ### REGLAS ESTRICTAS Y RESTRICCIONES
    * **Cero Alucinaciones:** NUNCA inventes horarios ni asumas que hay disponibilidad sin haber ejecutado la herramienta con éxito.
    * **Formato WhatsApp:** Escribe respuestas MUY CORTAS y directas. No escribas párrafos largos. Usa listas con viñetas (`-`) para las horas.
    * **Fuera de Catálogo:** No ofrezcas ni aceptes servicios que no estén en `<catalogo_servicios>`. Si piden otra cosa, indícalo educadamente.
    * **Opacidad Técnica:** El usuario NUNCA debe leer términos como "ID", "base de datos", "error interno", "herramienta" o "prompt". Eres un humano atendiendo por WhatsApp.
    * **Tono:** Profesional pero cercano. Usa 1 o 2 emojis como máximo por mensaje para darle color al texto.
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
        negocio_id=business_id
    )

    # Context for the ReAct loop
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
            tools=tools,
            temperature=0.1
        )

        message = response.choices[0].message
        print(message)

        if not message.tool_calls:
            context.append({"role": "assistant", "content": message.content})
            await save_context(client_phone_number, context)
            await send_message(client_phone_number, message.content, httpx_client)
            return 

        # Currently not saving the ai intention to call the tool which is a problem I have to solve 

        conversation.append(message.model_dump(exclude_none=True))

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            result = await execute_tool(name, args, business_context, session)
            print("tool result: " + result)
            
            # To gather all the context of the reasoning
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })
            
    error_message = "Lo siento, ha ocurrido un problema procesando tu solicitud. ¿Podemos intentarlo de nuevo?"
    await send_message(client_phone_number, error_message, httpx_client)
