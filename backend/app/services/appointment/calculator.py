from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

def subtract_sets(
    worker_hours: list, 
    worker_apps: list, 
    service_duration: timedelta, 
    requested_date: date, 
):
    candidate_slots = []
    free_slots = set()
    block_duration = timedelta(minutes=30)

    for turn in worker_hours:
        start = datetime.combine(requested_date, turn.start_time)
        end = datetime.combine(requested_date, turn.end_time)
        
        # We divide the hours in 30 minutes blocks
        while start + service_duration <= end:
            candidate_slots.append(start)
            start += block_duration

    # A slot is only free if [slot, slot + service_duration) does not overlap
    # any appointment, even when the slot starts before the appointment does.
    for slot in candidate_slots:
        slot_end = slot + service_duration
        overlaps = any(slot < app.end_time and slot_end > app.start_time for app in worker_apps)
        if not overlaps:
            free_slots.add(slot.strftime("%H:%M"))

    return free_slots

def hide_past_slots(result: list, requested_date: date, timezone: ZoneInfo):
    current_time = datetime.now(timezone)
    current_date = current_time.date()

    if requested_date < current_date:
        return []
    
    if requested_date > current_date:
        return result
    
    available_slots = []
    current_time_str = current_time.strftime("%H:%M")

    for hour_str in result:
        if current_time_str < hour_str: 
            available_slots.append(hour_str)
    
    return available_slots
