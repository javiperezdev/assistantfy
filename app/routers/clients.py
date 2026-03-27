from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.services.client_service import search_client_by_phone_number, create_client
from app.database import get_session

router = APIRouter()

# functions are synchronous because python's sqlite driver it's, but as it is really fast, we're talking of few ms there is no drama

'''
get_client is an ai tool in charge of searching a client by it's phone number.
It has a post method, because it is an ai tool
'''

@router.post("/client/{phone_number}")
def get_client(phone_number: str):
    return search_client_by_phone_number(phone_number)

'''
add_client, is a tool that ai uses to add clients to the database.
If they don't exist, they would be added to the database
If AI hallucinates and try to add a client that is already added, function would return the client
'''
 
@router.post("/client/{phone_number}")
def add_client(phone_number: str, name: str, session: Session = Depends(get_session)):
    client = search_client_by_phone_number(phone_number, session)
    if client is None:
        create_client()
    # AI should not get here, but I am using defensive programming here
    return client
