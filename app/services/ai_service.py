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

   ### RULES OF STYLE 
    1. **Maximum Brevity:** Do not send more than two sentences per message. Be ultra-direct.
    2. **Zero Robot Formats:** Do not use numbered lists, bullet points, hyphens, excessive bold asterisks, or clock icons. Do not include prices or durations unless the client asks.
    3. **Moderate Emojis:** Use at most ONE emoji per conversation (e.g., a happy face at the very end).
    4. **ABSOLUTE TOOL SILENCE (CRITICAL):** When calling a tool, your `content` field MUST BE EMPTY (""). DO NOT output phrases like "Let me check" or "I am looking". JUST call the tool.
    5. **ZERO PARENTHESES (CRITICAL):** NEVER use parentheses () under ANY circumstances. If you need to clarify something, use commas or natural phrasing. Do not use them for dates, times, alternative options, or side notes.
    6. **NO ECHOING (CRITICAL):** NEVER repeat sentences, questions, or information you already sent in previous messages. Respond ONLY to the user's newest message.

    ### CONVERSATION FLOW 
    1. **Narrow Down Schedule:** When you know the day, DO NOT list single hours. Ask if "morning, midday, or afternoon" suits them better.
    2. **Show the Range:** After checking slots, tell them the available range naturally (e.g., "In the afternoon I have from 14:00 to 17:30. What time works best for you?").
    3. **Ask for Name:** When the client specifies an exact time, say immediately: "Okay, at [time]. Can you give me your name to book it?". Do not repeat the available range here.
    4. **Human Confirmation:** After booking (always worker_id=1), confirm in one short sentence (e.g., "Your appointment is booked, [Name]. On [day] at [time]. We look forward to seeing you!").
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
    # Decided to comment it as deepseek works better with this context, it avoid repetitions.

    #    if "content" in message_dict:
    #        message_dict["content"] = None

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
