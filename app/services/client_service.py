from sqlmodel import select, Session
from app.models import Client

'''
search_client_by_phone_number is in charge of obtaining clients 
by phone number the reason of returning the first is
due to this query can return one row as most, as phone_number is unique
'''

async def search_client_by_phone_number(phone_number: str, session: Session):
    statement = select(Client).where(Client.phone_number == phone_number)
    result = await session.exec(statement)
    return result.first()

'''
create_client is in charge of creating clients an adding them to the database
'''
async def create_client(business_id: int, name: str, phone_number: str, session: Session):
    client = Client(business_id=business_id, phone_number=phone_number, name=name)
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client