import hashlib
import hmac
import json

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
