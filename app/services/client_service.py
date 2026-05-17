from sqlmodel import select, Session
from app.models import Client



async def search_client_by_phone_number(phone_number: str, session: Session):
    '''
    search_client_by_phone_number is in charge of obtaining clients 
    by phone number the reason of returning the first is
    due to this query can return one row as most, as phone_number is unique
    '''
    statement = select(Client).where(Client.phone_number == phone_number)
    result = await session.exec(statement)
    return result.first()


async def create_client(business_id: int, name: str, phone_number: str, session: Session):
    '''
    create_client is in charge of creating clients an adding them to the database
    '''
    client = Client(business_id=business_id, phone_number=phone_number, name=name)
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client