from sqlmodel import Field, SQLModel, Index, UniqueConstraint
from datetime import datetime, time
from enum import Enum

class Business(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    phone_number: str
    name: str 
    timezone: str

class BusinessHours(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    day_of_week: int # 1=Monday, 7=Sunday
    start_time: time 
    end_time: time
    is_active: bool = Field(default=True)

class Client(SQLModel, table=True):
    # A phone number is unique per business, not globally: the same person can be a
    # client of two different businesses.
    __table_args__ = (UniqueConstraint("business_id", "phone_number", name="uq_client_business_phone"),)
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    phone_number: str = Field(index=True)
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
    is_active: bool | None = Field(default=True)

class WorkerHours(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    worker_id: int = Field(foreign_key="worker.id")
    day_of_week: int # 1=Monday, 7=Sunday
    start_time: time
    end_time: time
    is_active: bool = Field(default=True)

class WorkerService(SQLModel, table=True):
    business_id: int = Field(primary_key=True, foreign_key="business.id")
    service_id: int = Field(primary_key=True, foreign_key="service.id")
    worker_id: int = Field(primary_key=True, foreign_key="worker.id")

class AppointmentState(str, Enum):
    BOOKED = "BOOKED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"

class Appointment(SQLModel, table=True):
    '''
    Appointment class has a composite index because in services/appointment_service get_available_slots method
    would be doing searches with them, and a barbershop won't have thousands of inserts daily, so it is really
    cost-effective architectural decision
    '''
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    service_id: int = Field(foreign_key="service.id")
    client_id: int = Field(foreign_key="client.id")
    worker_id: int = Field(foreign_key="worker.id")
    start_time: datetime
    end_time: datetime
    appointment_state: AppointmentState = Field(default=AppointmentState.BOOKED)

class AdminUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_id: int = Field(foreign_key="business.id")
    email: str = Field(unique=True, index=True)
    password: str 
    is_active: bool = Field(default=True)



