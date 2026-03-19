from sqlmodel import select, Session
from app.models import Client

'''
search_clients_by_phone_number is in charge of obtaining clients 
by phone number the reason of returning the first is
due to this query can return one row as most, as phone_number is unique
'''

def search_clients_by_phone_number(phone_number: str, session: Session):
    statement = select(Client).where(Client.phone_number == phone_number)
    result = session.exec(statement)
    return result.first()