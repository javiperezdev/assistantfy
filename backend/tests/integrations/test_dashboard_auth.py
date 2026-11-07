"""The dashboard routers must derive the tenant from the session, not the client.

Two guarantees, tested at the HTTP layer:
1. Every dashboard endpoint rejects an unauthenticated request with 401.
2. The tenant is taken from the session: a foreign ``business_id`` query param
   is ignored, so one admin can never read or write another business' data.
"""
import httpx
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Service
from app.scripts.create_admin import create_or_reset_admin

# (method, path, minimal valid params) so request validation passes and the
# auth dependency is the thing that answers. All values are strings to avoid
# httpx bool/int serialisation surprises.
DASHBOARD_ENDPOINTS = [
    ("GET", "/API/appointments", {"date": "2026-11-07"}),
    ("POST", "/API/appointments", {"phone_number": "311", "service_id": "1", "start_time": "2026-11-07T10:00:00"}),
    ("PATCH", "/API/appointment/state", {"appointment_id": "1", "new_state": "BOOKED"}),
    ("GET", "/API/services", {}),
    ("POST", "/API/service", {"service_name": "Cut", "price": "10", "duration_minutes": "30"}),
    ("DELETE", "/API/service", {"id": "1"}),
    ("GET", "/API/workers", {}),
    ("POST", "/API/worker", {"worker_name": "Bob"}),
    ("DELETE", "/API/worker", {"worker_id": "1"}),
    ("GET", "/API/worker-service", {}),
    ("POST", "/API/worker-service", {"service_id": "1", "worker_id": "1"}),
    ("DELETE", "/API/worker-service", {"service_id": "1", "worker_id": "1"}),
    ("GET", "/API/worker-hours", {"worker_id": "1"}),
    ("POST", "/API/worker-hours", {"worker_id": "1", "day_of_week": "1", "start_time": "09:00", "end_time": "17:00"}),
    ("PUT", "/API/worker-hours", {"id": "1", "worker_id": "1", "day_of_week": "1", "start_time": "09:00", "end_time": "17:00"}),
    ("PATCH", "/API/worker-hours/day", {"worker_id": "1", "day_of_week": "1", "is_active": "true"}),
    ("DELETE", "/API/worker-hours", {"id": "1", "worker_id": "1"}),
    ("GET", "/API/business-hours", {}),
    ("POST", "/API/business-hours", {"day_of_week": "1", "start_time": "09:00", "end_time": "17:00"}),
    ("DELETE", "/API/business-hours", {"id": "1"}),
    ("PUT", "/API/business-hours", {"id": "1", "day_of_week": "1", "start_time": "09:00", "end_time": "17:00"}),
]


@pytest.mark.parametrize(
    "method, path, params",
    DASHBOARD_ENDPOINTS,
    ids=[f"{m} {p}" for m, p, _ in DASHBOARD_ENDPOINTS],
)
async def test_dashboard_requires_auth(auth_client: httpx.AsyncClient, method, path, params):
    response = await auth_client.request(method, path, params=params)

    assert response.status_code == 401


async def test_dashboard_is_scoped_to_session_business(auth_client: httpx.AsyncClient, db_session: AsyncSession):
    admin_a, _ = await create_or_reset_admin(
        session=db_session,
        email="a@example.com",
        password="correct-horse-battery",
        business_name="Business A",
        business_phone="+34600000001",
    )
    admin_b, _ = await create_or_reset_admin(
        session=db_session,
        email="b@example.com",
        password="correct-horse-battery",
        business_name="Business B",
        business_phone="+34600000002",
    )

    db_session.add(Service(business_id=admin_a.business_id, name="A cut", price=10, duration_minutes=30))
    db_session.add(Service(business_id=admin_b.business_id, name="B cut", price=10, duration_minutes=30))
    await db_session.commit()

    await auth_client.post(
        "/API/auth/login",
        json={"email": "a@example.com", "password": "correct-horse-battery"},
    )

    response = await auth_client.get("/API/services")
    assert response.status_code == 200
    assert [s["name"] for s in response.json()] == ["A cut"]

    # A stale/foreign business_id query param must be ignored: still A's data.
    response = await auth_client.get("/API/services", params={"business_id": admin_b.business_id})
    assert response.status_code == 200
    assert [s["name"] for s in response.json()] == ["A cut"]
