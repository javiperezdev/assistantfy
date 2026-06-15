import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.services.ai_service import generate_response
from app.schemas.ai_tools import get_all_tool_definitions
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

@pytest.mark.asyncio
async def test_ai_tool_router_book_appointment(monkeypatch):
    # Mock AI Client
    mock_ai_client = AsyncMock()
    
    # Mock response to the client
    mock_message_tool = ChatCompletionMessage.model_validate({
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "book_appointment",
                    "arguments": json.dumps({
                        "worker_id": 1,
                        "service_id": 1,
                        "start_time": "2026-06-13T17:00:00"
                    })
                }
            }
        ]
    })
    
    mock_message_final = ChatCompletionMessage.model_validate({
        "role": "assistant",
        "content": "Booked!",
    })
    
    def side_effect(*args, **kwargs):
        if mock_ai_client.chat.completions.create.call_count == 1:
            return ChatCompletion(
                id="chat_1",
                choices=[Choice(finish_reason="tool_calls", index=0, message=mock_message_tool)],
                created=1, model="test", object="chat.completion"
            )
        return ChatCompletion(
            id="chat_2",
            choices=[Choice(finish_reason="stop", index=0, message=mock_message_final)],
            created=2, model="test", object="chat.completion"
        )
        
    mock_ai_client.chat.completions.create.side_effect = side_effect
    
    # Mock session and other dependencies
    mock_session = MagicMock()
    mock_httpx_client = AsyncMock()
    
    # We need to trigger the loop in generate_response.
    # The loop will call execute_tool, so we need to mock that too to avoid DB calls.
    
    monkeypatch.setattr("app.services.ai_service.execute_tool", AsyncMock(return_value={"status": "success"}))
    monkeypatch.setattr("app.services.ai_service.send_message", AsyncMock())
    monkeypatch.setattr("app.services.ai_service.add_to_context", AsyncMock())
    
    await generate_response(
        client_phone_number="123456",
        context=[{"role": "user", "content": "I want to book for tomorrow at 5pm"}],
        httpx_client=mock_httpx_client,
        ai_client=mock_ai_client,
        system_prompt="Test prompt",
        business_id=1,
        session=mock_session
    )
    
    # Verify tool was called
    assert mock_ai_client.chat.completions.create.call_count == 2
    
    # Verify tool call was present in first call
    # The messages list in the SECOND call will contain the tool calls from the first turn.
    call2_args = mock_ai_client.chat.completions.create.call_args_list[1].kwargs
    
    # call2_args["messages"] should be [system, user, assistant_with_tool, tool_response]
    assistant_message = call2_args["messages"][2]
    
    assert assistant_message["tool_calls"][0]["function"]["name"] == "book_appointment"
    
    # Verify arguments parsed
    args = json.loads(assistant_message["tool_calls"][0]["function"]["arguments"])
    assert args["worker_id"] == 1
    assert args["service_id"] == 1
    assert args["start_time"] == "2026-06-13T17:00:00"
