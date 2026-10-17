import pytest
from datetime import datetime, timedelta, date, time
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Appointment, AppointmentState, BusinessHours, Client, Service, Worker, WorkerHours, WorkerService
from app.services.appointment.commands import create_appointment_from_owner
from app.services.appointment.queries import get_appointments_for_day

# Everything is booked in the future, far enough that "cannot book in the past"
# never interferes with the cases this test is actually about.
FUTURE = datetime.now().replace(microsecond=0) + timedelta(days=30)


async def seed_basic(db_session: AsyncSession, business_id: int, name_prefix: str = ""):
    """One worker (with hours), one service they can do, one already-known client."""
    worker = Worker(business_id=business_id, name=f"{name_prefix}Worker")
    service = Service(business_id=business_id, name=f"{name_prefix}Haircut", price=10.0, duration_minutes=30)
    client = Client(business_id=business_id, phone_number=f"{name_prefix}3461112222", name=f"{name_prefix}Known Client")
    db_session.add_all([worker, service, client])
    await db_session.commit()
    await db_session.refresh(worker)
    await db_session.refresh(service)
    await db_session.refresh(client)

    db_session.add(WorkerService(business_id=business_id, worker_id=worker.id, service_id=service.id))
    for day in range(1, 8):
        db_session.add(WorkerHours(
            worker_id=worker.id, day_of_week=day,
            start_time=time.min, end_time=time.max,
            is_active=True,
        ))
    await db_session.commit()
    return worker, service, client


@pytest.mark.asyncio
async def test_unknown_phone_creates_client_and_appointment(db_session: AsyncSession, two_businesses):
    business_a, business_b = two_businesses
    worker, service, _ = await seed_basic(db_session, business_a.id)

    result = await create_appointment_from_owner(
        session=db_session, business_id=business_a.id, phone_number="3469998888",
        name="Brand New", service_id=service.id, worker_id=worker.id, start_time=FUTURE,
    )

    assert result["status"] == "success"
    new_client = (await db_session.exec(
        select(Client).where(Client.phone_number == "3469998888")
    )).first()
    assert new_client is not None
    assert new_client.name == "Brand New"

    appointments = await get_appointments_for_day(db_session, business_a.id, FUTURE.date())
    assert len(appointments) == 1
    assert appointments[0]["client_name"] == "Brand New"
    assert appointments[0]["appointment_state"] == AppointmentState.BOOKED


@pytest.mark.asyncio
async def test_known_phone_reuses_client_without_duplicates(db_session: AsyncSession, two_businesses):
    business_a, _ = two_businesses
    worker, service, client = await seed_basic(db_session, business_a.id)
    client_count_before = len((await db_session.exec(
        select(Client).where(Client.business_id == business_a.id)
    )).all())

    # Same phone as the seeded client, different name: the phone wins, no new row.
    result = await create_appointment_from_owner(
        session=db_session, business_id=business_a.id, phone_number=client.phone_number,
        name="Should Be Ignored", service_id=service.id, worker_id=worker.id, start_time=FUTURE,
    )

    assert result["status"] == "success"
    client_count_after = len((await db_session.exec(
        select(Client).where(Client.business_id == business_a.id)
    )).all())
    assert client_count_after == client_count_before

    appointments = await get_appointments_for_day(db_session, business_a.id, FUTURE.date())
    assert appointments[0]["client_name"] == "Known Client"


@pytest.mark.asyncio
async def test_missing_worker_id_picks_first_free_worker(db_session: AsyncSession, two_businesses):
    business_a, _ = two_businesses
    worker, service, _ = await seed_basic(db_session, business_a.id)

    result = await create_appointment_from_owner(
        session=db_session, business_id=business_a.id, phone_number="3467776666",
        name=None, service_id=service.id, worker_id=None, start_time=FUTURE,
    )

    assert result["status"] == "success"
    appointments = await get_appointments_for_day(db_session, business_a.id, FUTURE.date())
    assert len(appointments) == 1
    assert appointments[0]["worker_name"] == "Worker"


@pytest.mark.asyncio
async def test_overlap_returns_error_dict_not_exception(db_session: AsyncSession, two_businesses):
    business_a, _ = two_businesses
    worker, service, _ = await seed_basic(db_session, business_a.id)

    first = await create_appointment_from_owner(
        session=db_session, business_id=business_a.id, phone_number="3465554444",
        name=None, service_id=service.id, worker_id=worker.id, start_time=FUTURE,
    )
    assert first["status"] == "success"

    # Same worker, overlapping window: the workflow reports it, no IntegrityError leaks.
    second = await create_appointment_from_owner(
        session=db_session, business_id=business_a.id, phone_number="3465554445",
        name=None, service_id=service.id, worker_id=worker.id,
        start_time=FUTURE + timedelta(minutes=15),
    )

    assert second["status"] == "error"
    assert "slot" in second["message"].lower() or "available" in second["message"].lower()


@pytest.mark.asyncio
async def test_past_time_returns_error(db_session: AsyncSession, two_businesses):
    business_a, _ = two_businesses
    worker, service, _ = await seed_basic(db_session, business_a.id)

    result = await create_appointment_from_owner(
        session=db_session, business_id=business_a.id, phone_number="3463332222",
        name=None, service_id=service.id, worker_id=worker.id,
        start_time=datetime(2020, 1, 1, 10, 0),
    )

    assert result["status"] == "error"
    assert "past" in result["message"].lower()
