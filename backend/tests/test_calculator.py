from datetime import date, datetime, time, timedelta
from types import SimpleNamespace

from app.services.appointment.calculator import subtract_sets


def test_slot_overlapping_appointment_is_not_offered():
    d = date(2026, 9, 25)
    turn = SimpleNamespace(start_time=time(9, 0), end_time=time(18, 0))
    appt = SimpleNamespace(
        start_time=datetime.combine(d, time(10, 0)),
        end_time=datetime.combine(d, time(11, 0)),
    )

    slots = subtract_sets([turn], [appt], timedelta(minutes=60), d)

    # 09:30-10:30, 10:00-11:00 and 10:30-11:30 all overlap the appointment
    assert "09:30" not in slots
    assert "10:00" not in slots
    assert "10:30" not in slots
    # non-overlapping neighbours stay bookable
    assert "09:00" in slots
    assert "11:00" in slots
