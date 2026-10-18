import pytest
from datetime import date, datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Appointment, AppointmentState, Client, Service, Worker
from app.services.appointment.queries import get_appointments_for_day, get_client_appointments

@pytest.mark.asyncio
async def test_get_appointments_for_day_flattens_and_stays_in_tenant(db_session: AsyncSession, two_businesses):
    business_a, business_b = two_businesses

    worker_a = Worker(business_id=business_a.id, name="Worker A")
    client_a = Client(business_id=business_a.id, phone_number="111", name="John Doe")
    service_a = Service(business_id=business_a.id, name="Haircut", price=10.0, duration_minutes=45)
    db_session.add_all([worker_a, client_a, service_a])
    await db_session.commit()
    await db_session.refresh(worker_a)
    await db_session.refresh(client_a)
    await db_session.refresh(service_a)

    # Two appointments on the requested day (out of start_time order, so the
    # test also checks ORDER BY), one of them cancelled to check all states arrive.
    late = Appointment(
        business_id=business_a.id, service_id=service_a.id, client_id=client_a.id, worker_id=worker_a.id,
        start_time=datetime(2026, 6, 12, 16, 0), end_time=datetime(2026, 6, 12, 16, 45),
        appointment_state=AppointmentState.CANCELLED,
    )
    early = Appointment(
        business_id=business_a.id, service_id=service_a.id, client_id=client_a.id, worker_id=worker_a.id,
        start_time=datetime(2026, 6, 12, 9, 30), end_time=datetime(2026, 6, 12, 10, 15),
    )
    # A different day, and a different tenant: neither may show up.
    other_day = Appointment(
        business_id=business_a.id, service_id=service_a.id, client_id=client_a.id, worker_id=worker_a.id,
        start_time=datetime(2026, 6, 13, 9, 30), end_time=datetime(2026, 6, 13, 10, 15),
    )
    worker_b = Worker(business_id=business_b.id, name="Worker B")
    client_b = Client(business_id=business_b.id, phone_number="222", name="Pietro")
    service_b = Service(business_id=business_b.id, name="Beard trim", price=5.0, duration_minutes=30)
    db_session.add_all([worker_b, client_b, service_b])
    await db_session.commit()
    await db_session.refresh(worker_b)
    await db_session.refresh(client_b)
    await db_session.refresh(service_b)
    other_tenant = Appointment(
        business_id=business_b.id, service_id=service_b.id, client_id=client_b.id, worker_id=worker_b.id,
        start_time=datetime(2026, 6, 12, 9, 0), end_time=datetime(2026, 6, 12, 9, 30),
    )
    db_session.add_all([early, late, other_day, other_tenant])
    await db_session.commit()

    appointments = await get_appointments_for_day(db_session, business_a.id, date(2026, 6, 12))

    # Flattened shape the frontend expects, ordered by start_time, states included.
    assert appointments == [
        {
            "id": early.id,
            "client_name": "John Doe",
            "worker_name": "Worker A",
            "service_name": "Haircut",
            "duration_minutes": 45,
            "start_time": "09:30",
            # past BOOKED appointments are presented as COMPLETED on purpose
            # (the assumption and its corrections are covered in
            # test_appointment_state_changes.py)
            "appointment_state": "COMPLETED",
        },
        {
            "id": late.id,
            "client_name": "John Doe",
            "worker_name": "Worker A",
            "service_name": "Haircut",
            "duration_minutes": 45,
            "start_time": "16:00",
            "appointment_state": AppointmentState.CANCELLED,
        },
    ]

    # Tenant isolation: business B only sees its own row.
    appointments_b = await get_appointments_for_day(db_session, business_b.id, date(2026, 6, 12))
    assert [a["id"] for a in appointments_b] == [other_tenant.id]

    # An empty day is just an empty list.
    assert await get_appointments_for_day(db_session, business_a.id, date(2026, 6, 20)) == []


@pytest.mark.asyncio
async def test_unknown_business_returns_empty(db_session: AsyncSession, two_businesses):
    # No business row -> both day queries answer [] instead of trying to
    # compute "now" in a timezone that doesn't exist.
    assert await get_appointments_for_day(db_session, 99999, date(2026, 6, 12)) == []
    assert await get_client_appointments(db_session, "111", 99999) == []
