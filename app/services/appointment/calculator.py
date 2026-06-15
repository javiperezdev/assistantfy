from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

def subtract_sets(
    worker_hours: list, 
    worker_apps: list, 
    service_duration: timedelta, 
    requested_date: date, 
):
    base_slots = set()
    occupied_slots = set()
    block_duration = timedelta(minutes=30)

    for turn in worker_hours:
        start = datetime.combine(requested_date, turn.start_time)
        end = datetime.combine(requested_date, turn.end_time)
        
        # We divide the hours in 30 minutes blocks
        while start + service_duration <= end:
            base_slots.add(start.strftime("%H:%M"))
            start += block_duration

    for app in worker_apps:
        app_start = app.start_time
        app_end = app.end_time

        # Divide the appointment in 30 minutes block
        while app_start < app_end:
            occupied_slots.add(app_start.strftime("%H:%M"))
            app_start += block_duration

    return base_slots - occupied_slots 

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
