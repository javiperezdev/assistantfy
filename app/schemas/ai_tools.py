from pydantic import BaseModel, Field
from datetime import date
import json 

tools = []

class AvailableSlotsAiSchema(BaseModel):
    """
    Esta herramienta busca huecos libres. Usala solo cuando te pregunten por disponibilidad o quieran agendar una cita.
    """
    requested_date: date = Field(description="Fecha para la que el usuario pide cita en formato ISO 8601 (AAAA-MM-DD)")
    service_id: int = Field(description="ID númerico del servicio solicitado")
    business_id: int = Field(exclude=True)

schema_dict = AvailableSlotsAiSchema.model_json_schema()


if "business_id" in schema_dict.get("properties", {}):
    del schema_dict["properties"]["business_id"]
if "business_id" in schema_dict.get("required", []):
    schema_dict["required"].remove("business_id")

tool_definition = {
    "type": "function",
    "function": {
        "name": "get_next_available_slots_for_ai", 
        "description": AvailableSlotsAiSchema.__doc__.strip(), 
        "parameters": schema_dict
    }
}

tools = [tool_definition]


