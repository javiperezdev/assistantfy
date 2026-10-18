import pytest
from datetime import datetime, timedelta, time
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Appointment, AppointmentState, Client, Service, Worker
from app.services.appointment.commands import set_appointment_state
from app.services.appointment.queries import get_appointments_for_day

NOW = datetime.now().replace(microsecond=0)
YESTERDAY = (NOW - timedelta(days=1)).date()


async def seed_base(db_session: AsyncSession, business_id: int):
    """The FK chain an appointment needs: one worker, one service, one client."""
    worker = Worker(business_id=business_id, name="Worker")
    service = Service(business_id=business_id, name="Haircut", price=10.0, duration_minutes=30)
    client = Client(business_id=business_id, phone_number="3461112222", name="Known Client")
    db_session.add_all([worker, service, client])
    await db_session.commit()
    await db_session.refresh(worker)
    await db_session.refresh(service)
    await db_session.refresh(client)
    return worker, service, client


async def make_appointment(db_session: AsyncSession, worker, service, client,
                           start: datetime, state: AppointmentState = AppointmentState.BOOKED):
    appointment = Appointment(
        business_id=worker.business_id, service_id=service.id, client_id=client.id,
        worker_id=worker.id, start_time=start, end_time=start + timedelta(minutes=30),
        appointment_state=state,
    )
    db_session.add(appointment)
    await db_session.commit()
    await db_session.refresh(appointment)
    return appointment


@pytest.mark.asyncio
async def test_cancel_booked_appointment(db_session: AsyncSession, two_businesses):
    business_a, _ = two_businesses
    worker, service, client = await seed_base(db_session, business_a.id)
    appointment = await make_appointment(db_session, worker, service, client, NOW + timedelta(days=30))

    rows_changed = await set_appointment_state(
        session=db_session, appointment_id=appointment.id, business_id=business_a.id,
        new_state=AppointmentState.CANCELLED,
    )

    assert rows_changed == 1
    # and the GET reflects it
    day = (NOW + timedelta(days=30)).date()
    appointments = await get_appointments_for_day(db_session, business_a.id, day)
    assert appointments[0]["appointment_state"] == AppointmentState.CANCELLED


@pytest.mark.asyncio
async def test_unknown_id_and_other_business_change_nothing(db_session: AsyncSession, two_businesses):
    business_a, business_b = two_businesses
    worker, service, client = await seed_base(db_session, business_b.id)
    appointment = await make_appointment(db_session, worker, service, client, NOW + timedelta(days=30))

    # doesn't exist at all
    assert await set_appointment_state(db_session, 99999, business_a.id, AppointmentState.CANCELLED) == 0
    # belongs to business B, business A must not touch it (multitenancy)
    assert await set_appointment_state(db_session, appointment.id, business_a.id, AppointmentState.CANCELLED) == 0
    # untouched after both attempts
    refreshed = await db_session.get(Appointment, appointment.id)
    assert refreshed.appointment_state == AppointmentState.BOOKED


@pytest.mark.asyncio
async def test_past_booked_presented_as_completed_but_cancelled_stays(db_session: AsyncSession, two_businesses):
    business_a, _ = two_businesses
    worker, service, client = await seed_base(db_session, business_a.id)
    base = datetime.combine(YESTERDAY, time(10, 0))
    past_booked = await make_appointment(db_session, worker, service, client, base)
    past_cancelled = await make_appointment(
        db_session, worker, service, client, base + timedelta(hours=1), state=AppointmentState.CANCELLED,
    )

    appointments = await get_appointments_for_day(db_session, business_a.id, YESTERDAY)
    by_id = {a["id"]: a for a in appointments}

    # past BOOKED is presented as COMPLETED (the "assume the client came" guess)...
    assert by_id[past_booked.id]["appointment_state"] == "COMPLETED"
    # ...but the DB still holds the truth
    db_row = await db_session.get(Appointment, past_booked.id)
    assert db_row.appointment_state == AppointmentState.BOOKED
    # derivation only touches BOOKED: a past CANCELLED is left alone
    assert by_id[past_cancelled.id]["appointment_state"] == AppointmentState.CANCELLED
