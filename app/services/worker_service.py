from sqlmodel import Session, select
from app.models import WorkerService, WorkerHours,Appointment
from collections import defaultdict

async def get_workers_by_service(session: Session, service_id: int):
    '''
    Method that returns workers able to perform a requested service
    '''
    statement = select(WorkerService.worker_id).where(WorkerService.service_id == service_id)
    result = (await session.exec(statement)).all()
    return result

async def get_all_worker_hours(session: Session, worker_ids: list[int], day_of_week: int):
    '''
    Method that returns workers requested from a list containing their ids 
    for an specific day of the week
    '''
    statement = select(WorkerHours).where(WorkerHours.worker_id.in_(worker_ids)).where(WorkerHours.day_of_week == day_of_week)
    result = await session.exec(statement)
    return result.all()

def group_by_workers(objects_list: list[WorkerHours] | list[Appointment]):
    """
    Groups all the appointment/workerHours by worker id (example: {1: ["10:00"], 2: ["11:00", "12:00"]})
    """
    workers_grouped = defaultdict(list)
    for object in objects_list:
        workers_grouped[object.worker_id].append(object)
        
    return workers_grouped