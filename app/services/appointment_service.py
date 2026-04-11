from sqlmodel import select, Session
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from app.models import Appointment
from .service_service import get_service_by_id
from app.services.business_service import get_business_by_id
from app.services.worker_service import get_workers_by_service, get_all_worker_hours, group_by_workers
from app.schemas.ai_tools import AvailableSlotsAiSchema

async def get_next_available_slots_for_ai(requested_info: AvailableSlotsAiSchema, business_id: int, session: Session):
    max_days = 7
    current_date = requested_info.requested_date
    
    for _ in range(max_days):
        daily_slots = await get_available_slots(current_date, session, business_id, requested_info.service_id)
        
        if daily_slots:
            return {
                "status": "success",
                "date": current_date.isoformat(),
                "slots": daily_slots[:4]
            }
            
        current_date += timedelta(days=1)
        
    return {
        "status": "error", 
        "message": f"La agenda está completamente llena desde {current_date} hasta los próximos {max_days} días. Pide disculpas y pregúntale al cliente si quiere que busques a partir de la semana siguiente o en un mes en concreto.",
        "data": []
    }

async def create_appointment(business_id: int, client_id: int, service_id: int, worker_id: int, start_time: datetime, end_time: datetime, session: Session):
    appointment = Appointment(business_id=business_id, client_id=client_id, service_id=service_id, worker_id=worker_id, start_time=start_time, end_time=end_time)
    slot_exists = (await (session.exec(
        select(Appointment).where(
            Appointment.business_id == business_id,
            Appointment.worker_id == worker_id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time                               
    )))).first()

    if slot_exists:
        new_slots = await get_available_slots(
            start_time.date(),
            session, 
            business_id=business_id, 
            service_id=service_id
        )
    
        if not new_slots:
            return {
                "status": "error",
                "message": "El hueco solicitado acaba de ser ocupado y ya no quedan más citas libres para ese día. Dile al cliente que lo sientes y pregúntale si quiere buscar en otro día.",
                "data": []
            }

        return {
            "status": "error",
            "message": "Este hueco se ha acabado, ofrece las nuevas opciones en la variable 'data'",
            "data": new_slots
        }


    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return {
        "status": "success",
        "message": "La cita se ha guardado correctamente",
        "data": new_slots
    }


async def get_all_appointments(session: Session, workers_id: list[int], requested_date: date):
    start_of_day = datetime.combine(requested_date, time.min)
    end_of_day = datetime.combine(requested_date, time.max)
    statement = select(Appointment).where(Appointment.worker_id.in_(workers_id)).where(Appointment.start_time >= start_of_day, Appointment.end_time <= end_of_day)
    result = (await session.exec(statement)).all()
    return result
    
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

    # If it wasn't a working day it will return an empty set
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



async def get_available_slots(requested_date: date, session: Session, business_id: int, service_id: int):
    # Basic business information
    business = await get_business_by_id(session, business_id)
    if not business:
        return {"status" : "error", "message" : "El id introducido no esta adherido a ningún negocio."}
    tz = ZoneInfo(business.timezone)
    service = await get_service_by_id(session, service_id)
    duration = timedelta(minutes=service.duration_minutes)

    # Query to get all the workers that can perform the requested service
    worker_ids = await get_workers_by_service(session, service_id)

    all_hours = await get_all_worker_hours(session, worker_ids, requested_date.isoweekday())
    all_appointments = await get_all_appointments(session, worker_ids, requested_date)

    # We change the raw list of object to: { worker_id: [object_1, object2]} and so on
    hours_by_worker = group_by_workers(all_hours)
    apps_by_worker = group_by_workers(all_appointments)

    total_available_slots = set()

    for worker_id in worker_ids:
        worker_hours = hours_by_worker.get(worker_id, [])
        worker_apps = apps_by_worker.get(worker_id, [])
        
        slots_libres = subtract_sets(worker_hours, worker_apps, duration, requested_date)
        total_available_slots.update(slots_libres)     

    result = sorted(list(total_available_slots))
    return hide_past_slots(result, requested_date, tz)


   


    



    
    
