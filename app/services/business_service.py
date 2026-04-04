from sqlmodel import Session, select
from app.models import Business

async def get_business_by_id(session: Session, business_id: int):
    statement = select(Business).where(Business.id == business_id)
    result = await session.exec(statement)
    return result.first()
