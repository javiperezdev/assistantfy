from pydantic import BaseModel, Field
from datetime import date

tools = []

class AvailableSlotsSchema(BaseModel):
    """
    Esta herramienta busca huecos libres. Usala solo cuando te pregunten por disponibilidad o quieran agendar una cita.
    """
    requested_date: date = Field(description="Fecha para la que el usuario pide cita en formato ISO 8601 (AAAA-MM-DD)")
    service_id: int = Field(description="ID númerico del servicio solicitado")


schema_dict = AvailableSlotsSchema.model_json_schema()

tool_definition = {
    "type": "function",
    "function": {
        "name": "get_available_slots", 
        "description": AvailableSlotsSchema.__doc__.strip(), 
        "parameters": schema_dict
    }
}

tools = [tool_definition]


