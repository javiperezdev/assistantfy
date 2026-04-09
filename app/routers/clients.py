from fastapi import APIRouter, Depends, Response
from sqlmodel import Session
from app.services.client_service import search_client_by_phone_number, create_client
from app.database import get_session

router = APIRouter(tags=["Clients"])

'''
Not using router for the current phase
'''

@router.get("/client")
async def get_client(phone_number: str, response: Response, session: Session = Depends(get_session)):
    client =  await search_client_by_phone_number(phone_number, session)
    if not client:
        response.status_code = 404 
        return {
            "status": "error", 
            "message": f"El cliente con teléfono {phone_number} no existe en la base de datos."
        }

    return {
        "status": "success",
        "data": client
    }

 
@router.post("/client")
async def add_client(
    business_id: int,
    name: str, 
    phone_number: str, 
    response: Response, 
    session: Session = Depends(get_session)
):
    client = await search_client_by_phone_number(phone_number, session)
    
    if client:
        response.status_code = 200
        return {
            "status": "success",
            "message": "El cliente ya estaba registrado.",
            "data": client
        }
    
    new_client = await create_client(business_id, name, phone_number, session)
    
    response.status_code = 201
    return {
        "status": "success",
        "message": f"Cliente {name} registrado con éxito.",
        "data": new_client
    }
