from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  
from app.database import get_session
from app.services.worker_service import get_all_workers, add_worker, delete_worker

router = APIRouter(tags=["Worker"])

@router.get("/workers")
async def get_workers(business_id: int, session: AsyncSession = Depends(get_session)):
    workers = await get_all_workers(business_id, session)
    if len(workers) == 0:
        return []
    return workers

@router.post("/worker", status_code=status.HTTP_201_CREATED)
async def add_new_worker(business_id: int, worker_name: str, session: AsyncSession = Depends(get_session)):
    if worker_name == "":
        raise HTTPException(status_code=400, detail="Name couldn't be empty!")
    new_worker = await add_worker(business_id=business_id, name=worker_name, session=session)
    return new_worker

@router.delete("/worker", status_code=status.HTTP_200_OK)
async def remove_worker(business_id: int, worker_id: int, session: AsyncSession = Depends(get_session)):
    worker = await delete_worker(business_id=business_id, id=worker_id, session=session)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {"name" : worker.name}