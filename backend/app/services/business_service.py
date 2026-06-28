from sqlmodel import select
from app.models import Business
from sqlalchemy.ext.asyncio import AsyncSession

async def get_business_by_id(session: AsyncSession, business_id: int):
    """
    Qurey that returns business information from an id
    """
    statement = select(Business).where(Business.id == business_id)
    result = await session.exec(statement)
    return result.first()


async def get_id_by_phone_number(session: AsyncSession, phone_number: str):
    '''
    Query that returns the business id from phone number.
    This method is key because when having a request we would know the phone number of the 
    business not the id
    '''
    statement = select(Business.id).where(Business.phone_number == phone_number)
    result = await session.exec(statement)
    return result.first()


