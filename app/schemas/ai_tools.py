from pydantic import BaseModel, Field
from datetime import date
import json 

class get_next_available_slots_for_ai(BaseModel):
    """
    Esta herramienta busca huecos libres. Usala solo cuando te pregunten por disponibilidad o quieran agendar una cita.
    """
    requested_date: date = Field(description="Fecha para la que el usuario pide cita en formato ISO 8601 (AAAA-MM-DD)")
    service_id: int = Field(description="ID númerico del servicio solicitado")

json.dumps(get_next_available_slots_for_ai.model_json_schema(), indent=2, ensure_ascii=False)

tools = []

tools.append(get_next_available_slots_for_ai.model_json_schema())



