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

class Value(BaseModel):
    messages: list[Message] | None = None # It can be none, to avoid status calls
    statuses: list[dict] | None = None

class Change(BaseModel):
    value: Value | None = None

class Entry(BaseModel):
    changes: list[Change]

class WebhookBody(BaseModel):
    entry: list[Entry]
