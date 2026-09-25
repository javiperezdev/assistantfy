import pytest
from datetime import datetime, date
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Business, Worker, Appointment, Service, Client
from app.services.appointment.queries import get_all_appointments

@pytest.mark.asyncio
async def test_tenant_isolation_leak(db_session: AsyncSession):
    business_a = Business(phone_number="111", name="Business A", timezone="UTC")
    business_b = Business(phone_number="222", name="Business B", timezone="UTC")
    db_session.add(business_a)
    db_session.add(business_b)
    await db_session.commit()
    await db_session.refresh(business_a)
    await db_session.refresh(business_b)

    worker_a = Worker(business_id=business_a.id, name="Worker A")
    worker_b = Worker(business_id=business_b.id, name="Worker B")
    db_session.add(worker_a)
    db_session.add(worker_b)
    await db_session.commit()
    await db_session.refresh(worker_a)
    await db_session.refresh(worker_b)

    client_a = Client(business_id=business_a.id, phone_number="client_a")
    client_b = Client(business_id=business_b.id, phone_number="client_b")
    db_session.add(client_a)
    db_session.add(client_b)
    await db_session.commit()
    await db_session.refresh(client_a)
    await db_session.refresh(client_b)

    service_a = Service(business_id=business_a.id, name="Service A", price=10.0, duration_minutes=30)
    service_b = Service(business_id=business_b.id, name="Service B", price=20.0, duration_minutes=30)
    db_session.add(service_a)
    db_session.add(service_b)
    await db_session.commit()
    await db_session.refresh(service_a)
    await db_session.refresh(service_b)

    appt_a = Appointment(
        business_id=business_a.id,
        service_id=service_a.id,
        client_id=client_a.id,
        worker_id=worker_a.id,
        start_time=datetime(2026, 6, 12, 10, 0),
        end_time=datetime(2026, 6, 12, 10, 30),
    )
    appt_b = Appointment(
        business_id=business_b.id,
        service_id=service_b.id,
        client_id=client_b.id,
        worker_id=worker_b.id,
        start_time=datetime(2026, 6, 12, 10, 0),
        end_time=datetime(2026, 6, 12, 10, 30),
    )
    db_session.add(appt_a)
    db_session.add(appt_b)
    await db_session.commit()

    # Query using Business B's worker_id
    # We expect to only see Business B's appointments
    apps_for_worker_b = await get_all_appointments(db_session, [worker_b.id], date(2026, 6, 12), business_b.id)
    
    assert len(apps_for_worker_b) == 1
    assert apps_for_worker_b[0].id == appt_b.id
    assert apps_for_worker_b[0].business_id == business_b.id

    # If a malicious or buggy actor passes Worker A's ID to a service/query 
    # intended for Business B (without checking the business_id), they get Business A's data.
    
    # If we pass business_b.id but worker_a.id (belonging to business_a), we should get 0 results.
    apps_leak_attempt = await get_all_appointments(db_session, [worker_a.id], date(2026, 6, 12), business_b.id)
    assert len(apps_leak_attempt) == 0
    