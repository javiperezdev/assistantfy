import hashlib
import hmac
import json
from unittest.mock import AsyncMock

from app.config import settings


def _sign(raw_body: bytes) -> dict:
    digest = hmac.new(settings.meta_app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return {
        "X-Hub-Signature-256": f"sha256={digest}",
        "Content-Type": "application/json",
    }


def test_webhook_post(client):
    # Mock meta response
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {
                                "display_phone_number": "123456",
                                "phone_number_id": "789"
                            },
                            "messages": [
                                {
                                    "from": "111222333",
                                    "text": {"body": "Hello"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    raw_body = json.dumps(payload).encode()

    # We act as meta sending to our server the request, signature included
    response = client.post("/webhook", content=raw_body, headers=_sign(raw_body))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_unknown_business_returns_ok_without_replying(client, monkeypatch):
    import app.routers.whatsapp as whatsapp_router

    async def _no_business(session, phone_number):
        return None

    monkeypatch.setattr(whatsapp_router, "get_id_by_phone_number", _no_business)
    send_mock = AsyncMock()
    monkeypatch.setattr(whatsapp_router, "send_message", send_mock)

    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {
                                "display_phone_number": "999999",
                                "phone_number_id": "789"
                            },
                            "messages": [
                                {
                                    "from": "111222333",
                                    "text": {"body": "Hello"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    raw_body = json.dumps(payload).encode()

    response = client.post("/webhook", content=raw_body, headers=_sign(raw_body))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    send_mock.assert_not_awaited()


def test_webhook_rejects_missing_signature(client):
    response = client.post("/webhook", json={"entry": []})

    assert response.status_code == 403


def test_webhook_rejects_wrong_signature(client):
    raw_body = json.dumps({"entry": []}).encode()
    headers = _sign(raw_body)
    headers["X-Hub-Signature-256"] = "sha256=" + "0" * 64

    response = client.post("/webhook", content=raw_body, headers=headers)

    assert response.status_code == 403


def test_webhook_rejects_tampered_body(client):
    raw_body = json.dumps({"entry": []}).encode()
    headers = _sign(raw_body)
    tampered = json.dumps({"entry": [], "extra": True}).encode()

    response = client.post("/webhook", content=tampered, headers=headers)

    assert response.status_code == 403
