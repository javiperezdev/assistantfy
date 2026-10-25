import pytest
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from app.models import Business, Client, Service, Worker, WorkerHours, WorkerService, Appointment, AppointmentState
from app.services.worker_service import get_workers_by_service, get_first_available_worker
from app.services.worker_hours_service import get_worker_hours, delete_worker_hour, create_worker_hours, update_worker_hours, toggle_day
from app.services.worker_service_service import get_worker_services
from app.services.appointment.validators import validate_appointment_creation


async def seed_business_with_two_workers(db_session):
    business = Business(phone_number="123", name="test", timezone="UTC")
    db_session.add(business)
    await db_session.flush()

    service = Service(business_id=business.id, name="service", price=10, duration_minutes=60)
    active_worker = Worker(business_id=business.id, name="active")
    inactive_worker = Worker(business_id=business.id, name="inactive", is_active=False)
    db_session.add_all([service, active_worker, inactive_worker])
    await db_session.flush()

    for worker in (active_worker, inactive_worker):
        db_session.add(WorkerService(business_id=business.id, service_id=service.id, worker_id=worker.id))
    await db_session.flush()
    return business, service, active_worker, inactive_worker


@pytest.mark.asyncio
async def test_get_workers_by_service_excludes_inactive_workers(db_session):
    business, service, active_worker, inactive_worker = await seed_business_with_two_workers(db_session)

    worker_ids = await get_workers_by_service(db_session, service.id, business.id)

    assert list(worker_ids) == [active_worker.id]


@pytest.mark.asyncio
async def test_get_worker_services_excludes_inactive_workers(db_session):
    business, service, active_worker, inactive_worker = await seed_business_with_two_workers(db_session)

    assignments = await get_worker_services(db_session, business.id)

    assert assignments == {service.id: [active_worker.id]}


@pytest.mark.asyncio
async def test_validate_appointment_creation_rejects_inactive_worker(db_session):
    business, service, active_worker, inactive_worker = await seed_business_with_two_workers(db_session)

    result = await validate_appointment_creation(
        db_session, business.id, service.id, inactive_worker.id, datetime(2027, 6, 12, 10, 0)
    )

    result_active = await validate_appointment_creation(
        db_session, business.id, service.id, active_worker.id, datetime(2027, 6, 12, 10, 0)
    )

    assert result["status"] == "error"
    assert result_active["status"] == "success"


@pytest.mark.asyncio
async def test_get_and_delete_worker_hours(db_session):
    business, service, active_worker, inactive_worker = await seed_business_with_two_workers(db_session)
    other_business = Business(phone_number="322", name="other", timezone="UTC")
    db_session.add(other_business)
    await db_session.flush()
    other_worker = Worker(business_id=other_business.id, name="other")
    db_session.add(other_worker)
    await db_session.flush()

    monday_late = WorkerHours(worker_id=active_worker.id, day_of_week=1, start_time=time(14, 0), end_time=time(18, 0))
    monday_morning = WorkerHours(worker_id=active_worker.id, day_of_week=1, start_time=time(9, 0), end_time=time(13, 0))
    other_slot = WorkerHours(worker_id=other_worker.id, day_of_week=1, start_time=time(9, 0), end_time=time(17, 0))
    db_session.add_all([monday_late, monday_morning, other_slot])
    await db_session.flush()

    hours = await get_worker_hours(active_worker.id, business.id, db_session)
    assert [(h.day_of_week, h.start_time) for h in hours] == [(1, time(9, 0)), (1, time(14, 0))]

    # Tenant boundary: another business can't see or delete this slot
    assert await get_worker_hours(active_worker.id, other_business.id, db_session) == []
    assert await delete_worker_hour(monday_morning.id, active_worker.id, other_business.id, db_session) is None

    deleted = await delete_worker_hour(monday_morning.id, active_worker.id, business.id, db_session)
    assert deleted.id == monday_morning.id
    hours = await get_worker_hours(active_worker.id, business.id, db_session)
    assert [h.id for h in hours] == [monday_late.id]


@pytest.mark.asyncio
async def test_create_and_update_worker_hours(db_session):
    business, service, active_worker, inactive_worker = await seed_business_with_two_workers(db_session)
    other_business = Business(phone_number="322", name="other", timezone="UTC")
    db_session.add(other_business)
    await db_session.flush()

    # Tenant boundary: can't create hours for another business's worker
    assert await create_worker_hours(active_worker.id, other_business.id, 2, time(9, 0), time(17, 0), db_session) is None

    hour = await create_worker_hours(active_worker.id, business.id, 2, time(9, 0), time(17, 0), db_session)
    assert (hour.day_of_week, hour.start_time, hour.end_time) == (2, time(9, 0), time(17, 0))

    updated = await update_worker_hours(hour.id, active_worker.id, business.id, 3, time(10, 0), time(16, 0), db_session)
    assert (updated.day_of_week, updated.start_time, updated.end_time) == (3, time(10, 0), time(16, 0))

    # Tenant boundary: another business can't touch this slot
    assert await update_worker_hours(hour.id, active_worker.id, other_business.id, 1, time(8, 0), time(9, 0), db_session) is None
    hours = await get_worker_hours(active_worker.id, business.id, db_session)
    assert (hours[0].day_of_week, hours[0].start_time) == (3, time(10, 0))


@pytest.mark.asyncio
async def test_toggle_day_is_scoped_by_business(db_session):
    business, service, active_worker, inactive_worker = await seed_business_with_two_workers(db_session)
    other_business = Business(phone_number="322", name="other", timezone="UTC")
    db_session.add(other_business)
    await db_session.flush()

    # Tenant boundary: another business can't toggle this worker's day (None -> 404)
    assert await toggle_day(active_worker.id, other_business.id, 1, False, db_session) is None

    # Day with no record yet -> creates it active
    created = await toggle_day(active_worker.id, business.id, 1, True, db_session)
    assert (created.day_of_week, created.is_active) == (1, True)

    # Existing record -> flips it (rowcount), and the day stops being listed
    assert await toggle_day(active_worker.id, business.id, 1, False, db_session) == 1
    assert await get_worker_hours(active_worker.id, business.id, db_session) == []


# --- get_first_available_worker ------------------------------------------------
# Reference slot: Monday 2027-06-14 10:00-11:00 UTC (isoweekday() == 1)

MONDAY_10 = datetime(2027, 6, 14, 10, 0, tzinfo=ZoneInfo("UTC"))


async def seed_availability(db_session, timezone="UTC", worker_count=2, hours=True, day_of_week=1):
    business = Business(phone_number="123", name="test", timezone=timezone)
    db_session.add(business)
    await db_session.flush()

    service = Service(business_id=business.id, name="service", price=10, duration_minutes=60)
    client = Client(business_id=business.id, phone_number="555", name="client")
    db_session.add_all([service, client])
    await db_session.flush()

    workers = []
    for i in range(worker_count):
        worker = Worker(business_id=business.id, name=f"w{i}")
        db_session.add(worker)
        await db_session.flush()
        db_session.add(WorkerService(business_id=business.id, service_id=service.id, worker_id=worker.id))
        if hours:
            db_session.add(WorkerHours(worker_id=worker.id, day_of_week=day_of_week,
                                       start_time=time(9, 0), end_time=time(17, 0)))
        workers.append(worker)
    await db_session.flush()
    return business, service, client, workers


async def add_appointment(db_session, business, service, client, worker, start, minutes=60):
    # Appointments are stored as naive business-local timestamps (TIMESTAMP WITHOUT TIME ZONE).
    local_start = start.astimezone(ZoneInfo(business.timezone)).replace(tzinfo=None)
    appointment = Appointment(business_id=business.id, service_id=service.id, client_id=client.id,
                              worker_id=worker.id, start_time=local_start,
                              end_time=local_start + timedelta(minutes=minutes))
    db_session.add(appointment)
    await db_session.flush()
    return appointment


@pytest.mark.asyncio
async def test_returns_free_worker_inside_hours(db_session):
    business, service, client, (w1, _) = await seed_availability(db_session)

    worker_id = await get_first_available_worker(db_session, service.id, MONDAY_10, 60, business.id)

    assert worker_id == w1.id


@pytest.mark.asyncio
async def test_naive_start_time_is_read_as_business_local(db_session):
    business, service, client, _ = await seed_availability(
        db_session, timezone="America/Argentina/Buenos_Aires"
    )

    # Naive input == business-local time: 10:00 local is inside hours...
    ok = await get_first_available_worker(db_session, service.id, MONDAY_10.replace(tzinfo=None), 60, business.id)
    # ...and 19:00 local (22:00 UTC) is outside them.
    late = await get_first_available_worker(
        db_session, service.id, MONDAY_10.replace(hour=22, tzinfo=None), 60, business.id
    )

    assert ok is not None
    assert late is None


@pytest.mark.asyncio
async def test_returns_none_outside_working_hours(db_session):
    business, service, client, _ = await seed_availability(db_session)

    worker_id = await get_first_available_worker(
        db_session, service.id, MONDAY_10.replace(hour=18), 60, business.id
    )

    assert worker_id is None


@pytest.mark.asyncio
async def test_returns_none_when_hours_row_is_inactive(db_session):
    business, service, client, (worker, _) = await seed_availability(db_session, hours=False)
    db_session.add(WorkerHours(worker_id=worker.id, day_of_week=1,
                               start_time=time(9, 0), end_time=time(17, 0), is_active=False))
    await db_session.flush()

    assert await get_first_available_worker(db_session, service.id, MONDAY_10, 60, business.id) is None


@pytest.mark.asyncio
async def test_skips_worker_with_overlapping_appointment(db_session):
    business, service, client, (busy, free) = await seed_availability(db_session)
    await add_appointment(db_session, business, service, client, busy, MONDAY_10 + timedelta(minutes=30))

    worker_id = await get_first_available_worker(db_session, service.id, MONDAY_10, 60, business.id)

    assert worker_id == free.id


@pytest.mark.asyncio
async def test_only_busy_worker_means_no_availability(db_session):
    business, service, client, workers = await seed_availability(db_session, worker_count=1)
    await add_appointment(db_session, business, service, client, workers[0], MONDAY_10 + timedelta(minutes=30))

    assert await get_first_available_worker(db_session, service.id, MONDAY_10, 60, business.id) is None


@pytest.mark.asyncio
async def test_picks_least_busy_worker_of_free_candidates(db_session):
    business, service, client, (loaded, idle) = await seed_availability(db_session)
    # Both are free at 10:00, but `loaded` already has a later booking today.
    await add_appointment(db_session, business, service, client, loaded, MONDAY_10.replace(hour=15))

    worker_id = await get_first_available_worker(db_session, service.id, MONDAY_10, 60, business.id)

    assert worker_id == idle.id


@pytest.mark.asyncio
async def test_working_hours_use_business_timezone(db_session):
    business, service, client, _ = await seed_availability(db_session, timezone="America/Argentina/Buenos_Aires")

    # 22:00 UTC == 19:00 in Buenos Aires -> outside the 9-17 hours there.
    late = await get_first_available_worker(db_session, service.id, MONDAY_10.replace(hour=22), 60, business.id)
    # 13:00 UTC == 10:00 in Buenos Aires -> inside hours.
    ok = await get_first_available_worker(db_session, service.id, MONDAY_10.replace(hour=13), 60, business.id)

    assert late is None
    assert ok is not None


@pytest.mark.asyncio
async def test_ignores_cancelled_appointments(db_session):
    business, service, client, workers = await seed_availability(db_session, worker_count=1)
    cancelled = await add_appointment(db_session, business, service, client, workers[0], MONDAY_10 + timedelta(minutes=30))
    cancelled.appointment_state = AppointmentState.CANCELLED
    await db_session.flush()

    worker_id = await get_first_available_worker(db_session, service.id, MONDAY_10, 60, business.id)

    assert worker_id == workers[0].id
