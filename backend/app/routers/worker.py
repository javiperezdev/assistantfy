from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.services.worker_service import get_all_workers

router = APIRouter(tags=["workers"])

@router.get("/workers")
async def getWorkers(business_id: int, session: Session = Depends(get_session)):
    workers = await get_all_workers(business_id, session)
    if len(workers) == 0:
        raise HTTPException(status_code=404, detail="No workers were found")
    return workers