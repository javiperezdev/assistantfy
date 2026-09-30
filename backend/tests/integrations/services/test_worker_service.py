import pytest
from datetime import datetime, time
from app.models import Business, Service, Worker, WorkerHours, WorkerService
from app.services.worker_service import get_workers_by_service
from app.services.worker_hours_service import get_worker_hours, delete_worker_hour, create_worker_hours, update_worker_hours
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
