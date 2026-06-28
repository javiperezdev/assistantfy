import pytest
from app.models import Appointment, Business, Worker, Service, Client
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

@pytest.mark.asyncio
async def test_multi_booking_exclusion(db_session):
    # Setup necessary entities
    # flush() to assign them an id automatically
    business = Business(phone_number="123", name="test", timezone="UTC")
    db_session.add(business)
    await db_session.flush()
    
    worker = Worker(, business_id=business.id, name="worker")
    db_session.add(worker)
    await db_session.flush()

    service = Service(business_id=business.id, name="service", price=10, duration_minutes=60)
    db_session.add(service)
    await db_session.flush()

    client = Client(business_id=business.id, phone_number="456")
    db_session.add(client)
    await db_session.flush()
    
    appointment1 = Appointment(
        business_id=business.id,
        service_id=service.id,
        client_id=client.id,
        worker_id=worker.id,
        start_time=datetime(2026, 6, 12, 10, 0),
        end_time=datetime(2026, 6, 12, 11, 0)
    )
    
    appointment2 = Appointment(
        business_id=business.id,
        service_id=service.id,
        client_id=client.id,
        worker_id=worker.id,
        start_time=datetime(2026, 6, 12, 10, 30),
        end_time=datetime(2026, 6, 12, 11, 30)
    )
    
    db_session.add(appointment1)
    await db_session.commit()
    
    db_session.add(appointment2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
