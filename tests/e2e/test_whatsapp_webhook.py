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
    
    # We act as meta sending to our server the request
    response = client.post("/webhook", json=payload)
        
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
