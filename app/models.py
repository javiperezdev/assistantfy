from sqlmodel import Field, SQLModel, Index
from datetime import datetime, time

class Business(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    timezone: str

class BusinessHours(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    day_of_week: int 
    start_time: time 
    end_time: time

class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    phone_number: str = Field(unique=True)
    name: str | None = None

class Service(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    price: float 
    name: str
    duration_minutes: int

class Worker(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    name: str

class WorkerService(SQLModel, table=True):
    service_id: int = Field(primary_key=True, foreign_key="service.id")
    worker_id: int = Field(primary_key=True, foreign_key="worker.id")

'''
Appointment class has a composite index because in services/appointment_service get_available_slots method
would be doing searches with them, and a barbershop won't have thousands of inserts daily, so it is really
cost-effective architectural decision
'''
class Appointment(SQLModel, table=True):
    __tablename__ = "appointment"
    __tableargs__ = (
        Index("ix_appointment_dates", "start_datetime", "end_datetime")
    )
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    service_id: int = Field(foreign_key="service.id")
    client_id: int = Field(foreign_key="client.id")
    worker_id: int = Field(foreign_key="worker.id")
    start_time: datetime
    end_time: datetime



