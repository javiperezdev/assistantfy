import pytest
from datetime import datetime
from app.models import Business, Service, Worker, WorkerService
from app.services.worker_service import get_workers_by_service
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
