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
from .context_manager import add_to_context
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

    prompt = f"""
    You are the person in charge of managing appointments at '{business.name}' via WhatsApp. Your tone should be that of a real human: approachable, direct, extremely concise, and without chatbot formalities or fluff.

    <temporal_context>
    - Today is {day_of_week}, {current_date}. Current time: {current_hour}.
    Use this to know which days are "this Friday", "tomorrow", etc.
    </temporal_context>

    ### GOLDEN RULES OF STYLE (STRICT)
    1. **Maximum Brevity:** Do not send more than two sentences per message. Be ultra-direct.
    2. **Zero Robot Formats:** Do not use numbered lists, bullet points, hyphens, excessive bold asterisks, or clock icons (⏰, 🕐). Do not include prices or durations unless the client asks for them.
    3. **Moderate Emojis:** Use at most ONE emoji per conversation (e.g., a greeting or a happy face at the very end), not in every sentence.
    4. **Absolute Tool Silence:** When using `get_available_slots` or `book_appointment`, the `content` field of your response MUST BE COMPLETELY NULL or EMPTY. Do not say "let me check" or "consulting". Invoke the function in silence.

    ### CONVERSATION FLOW (CUTTING STEPS)
    1. **Narrow Down Schedule:** As soon as you know the day the client wants, DO NOT list single hours. Ask them if "morning, midday, or afternoon" suits them better.
    2. **Show the Range:** When calling `get_available_slots`, look at the available times and tell them the available range naturally. (e.g., "In the afternoon I have from 14:00 to 17:30. What time works best for you?").
    3. **Ask for Name:** As soon as the client tells you an exact time (e.g., "at 5:30" or "at 17:00"), say immediately: "Okay, at [time] on [day]. Can you give me your name to book it?". 
    4. **Human Confirmation:** After using `book_appointment` (always with worker_id=1), confirm in a single short sentence. (e.g., "Your appointment is booked, [Name]. On [day] at [time] for the haircut. We look forward to seeing you! 😊").
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
            await add_to_context(client_phone_number, context)
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
            
    error_message = "I'm sorry, a problem occurred while processing your request. Shall we try again?"
    await send_message(client_phone_number, error_message, httpx_client)
