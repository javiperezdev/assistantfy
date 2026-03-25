from datetime import date
from pydantic import BaseModel, Field
from config import availabily_schema_prompt

class CheckAvailabilitySchema(BaseModel):
    requested_date: date = Field(
        description=availabily_schema_prompt
    )