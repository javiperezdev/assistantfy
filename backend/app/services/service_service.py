from app.models import Service
from sqlmodel import Session, select

async def get_time_from_service(service_id: int, session: Session):
    statement = select(Service.duration_minutes).where(Service.id == service_id)
    result = await session.exec(statement)
    return result.first()

async def get_service_by_id(session: Session, id: int):
    statement = select(Service).where(Service.id == id)
    result = await session.exec(statement)
    return result.first()

async def get_services_catalog(business_id: int, session: Session):
    statement = select(Service).where(Service.business_id == business_id)
    services = await session.exec(statement)
    
    services_list = []
    for s in services:
        services_list.append(f"- **[ID: {s.id}]** {s.name} | {s.duration_minutes} mins | {s.price}€")
        
    list_format = "\n".join(services_list)

    if len(services_list) == 1:
        unique_service = services_list[0]
        return f"""
        - This business offers a SINGLE generic service.
        - DO NOT ask the client what service they want. Assume directly that they want a normal appointment.
        - When using the 'check_availability_tool', ALWAYS pass the service_id: {unique_service.id}.
        """
    
    return f"""
    - This is our service catalog:
    <service_catalog>
    {list_format}
    </service_catalog>
    - If you don't know what service the client wants, ASK THEM.
    - Use the numerical ID from the catalog when calling the tool.
    """

