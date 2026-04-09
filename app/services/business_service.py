from sqlmodel import Session, select
from app.models import Business
from async_lru import alru_cache

async def get_business_by_id(session: Session, business_id: int):
    statement = select(Business).where(Business.id == business_id)
    result = await session.exec(statement)
    return result.first()

'''
Method in charge of giving the business id to all the methods that need it in the lifespan
'''

@alru_cache(maxsize=500)
async def get_id_by_phone_number(session: Session, phone_number: str):
    statement = select(Business.id).where(Business.phone_number == phone_number)
    result = await session.exec(statement)
    return result.first()


