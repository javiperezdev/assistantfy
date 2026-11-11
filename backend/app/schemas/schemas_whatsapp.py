from pydantic import BaseModel, Field

'''
Path to validate messages from meta json (Currently only accepting text messages)
'''
class Text(BaseModel):
    body: str

# 'text' attribute accepts None because there are some cases, where we won't receive text (audio, img...) 

class Message(BaseModel):
    phone_number: str = Field(alias="from")
    text: Text | None = None

class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str

class Value(BaseModel):
    messages: list[Message] | None = None # It can be none, to avoid status calls
    metadata: Metadata | None = None      # None on account_update/config events
    statuses: list[dict] | None = None

class Change(BaseModel):
    field: str | None = None  # Meta's discriminator: "messages", "account_update", ...
    value: Value | None = None

class Entry(BaseModel):
    changes: list[Change]

class WebhookBody(BaseModel):
    entry: list[Entry]

# Object that contains the context 

class WhatsappContext(BaseModel):
    business_phone_number: str = Field(default=None)
    client_phone_number: str = Field(default=None)
    business_id: int = Field(default=None)