import pytest
from datetime import datetime, date, time
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import BusinessHours, Worker, Appointment, Service, Client
from app.services.appointment.queries import get_all_appointments
from app.services.appointment.commands import cancel_appointment_workflow
from app.services.client_service import search_client_by_phone_number
from app.services.service_service import get_service_by_id, get_time_from_service
from app.services.business_hours_service import update_business_hours, delete_business_hours

@pytest.mark.asyncio
async def test_tenant_isolation_leak(db_session: AsyncSession, two_businesses):
    business_a, business_b = two_businesses

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


@pytest.mark.asyncio
async def test_lookups_and_cancel_are_scoped_by_business(db_session: AsyncSession, two_businesses):
    business_a, business_b = two_businesses

    service_a = Service(business_id=business_a.id, name="Service A", price=10.0, duration_minutes=30)
    worker_a = Worker(business_id=business_a.id, name="Worker A")
    db_session.add_all([service_a, worker_a])
    await db_session.commit()
    await db_session.refresh(service_a)
    await db_session.refresh(worker_a)

    # The same phone number is a client of both businesses (unique per business, not global).
    client_a = Client(business_id=business_a.id, phone_number="345")
    client_b = Client(business_id=business_b.id, phone_number="345")
    db_session.add_all([client_a, client_b])
    await db_session.commit()
    await db_session.refresh(client_a)

    appt_a = Appointment(
        business_id=business_a.id,
        service_id=service_a.id,
        client_id=client_a.id,
        worker_id=worker_a.id,
        start_time=datetime(2027, 6, 12, 10, 0),
        end_time=datetime(2027, 6, 12, 10, 30),
    )
    db_session.add(appt_a)
    await db_session.commit()
    await db_session.refresh(appt_a)

    # Lookups never cross the tenant boundary, even with a valid id/phone from another tenant.
    assert (await search_client_by_phone_number("345", business_a.id, db_session)).id == client_a.id
    assert (await search_client_by_phone_number("345", business_b.id, db_session)).id == client_b.id
    assert await get_service_by_id(db_session, service_a.id, business_b.id) is None
    assert await get_time_from_service(service_a.id, business_b.id, db_session) is None

    # Business B cannot cancel an appointment of business A, even knowing its id.
    wrong_tenant = await cancel_appointment_workflow(
        session=db_session, appointment_id=appt_a.id, client_phone_number="345", business_id=business_b.id
    )
    assert wrong_tenant["status"] == "error"
    assert await db_session.get(Appointment, appt_a.id) is not None

    own_tenant = await cancel_appointment_workflow(
        session=db_session, appointment_id=appt_a.id, client_phone_number="345", business_id=business_a.id
    )
    assert own_tenant["status"] == "success"
    assert await db_session.get(Appointment, appt_a.id) is None


@pytest.mark.asyncio
async def test_business_hours_mutations_are_scoped_by_business(db_session: AsyncSession, two_businesses):
    business_a, business_b = two_businesses

    hours_a = BusinessHours(business_id=business_a.id, day_of_week=1, start_time=time(9, 0), end_time=time(18, 0))
    db_session.add(hours_a)
    await db_session.commit()
    await db_session.refresh(hours_a)

    # Business B cannot update or soft-delete business A's row by id.
    assert await update_business_hours(hours_a.id, business_b.id, 2, time(10, 0), time(17, 0), db_session) is None
    assert await delete_business_hours(hours_a.id, business_b.id, db_session) is None

    updated = await update_business_hours(hours_a.id, business_a.id, 2, time(10, 0), time(17, 0), db_session)
    assert updated is not None and updated.day_of_week == 2
    