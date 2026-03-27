from datetime import date, datetime
from pydantic import BaseModel, Field
from enum import Enum

# Creamos una lista cerrada para que la IA no se invente servicios
class ServiceType(str, Enum):
    CORTE = "corte"
    TINTE = "tinte"
    BARBA = "barba"
    CORTE_Y_BARBA = "corte_y_barba"

class BookAppointmentSchema(BaseModel):
    client_name: str = Field(
        description="Nombre del cliente. Si no lo sabes, pregúntaselo antes de usar esta herramienta."
    )
    
    start_time: datetime = Field(
        description="Fecha y hora de inicio de la cita en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)."
    )
    
    service: ServiceType = Field(
        description="Tipo de servicio que desea el cliente."
    )

class CheckAvailabilitySchema(BaseModel):
    requested_date: date = Field(
        description=""
    )
