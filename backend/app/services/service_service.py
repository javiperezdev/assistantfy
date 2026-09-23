from app.models import Service
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_time_from_service(service_id: int, session: AsyncSession):
    statement = select(Service.duration_minutes).where(Service.id == service_id)
    result = await session.exec(statement)
    return result.first()

async def get_service_by_id(session: AsyncSession, id: int):
    statement = select(Service).where(Service.id == id)
    result = await session.exec(statement)
    return result.first()

async def get_all_services(business_id: int, session: AsyncSession):
    statement = select(Service).where(Service.business_id == business_id)
    result = await session.exec(statement)
    return result.all()

async def create_service(business_id: int, name: str, price: int, duration_minutes: int, session: AsyncSession):
    service = Service(business_id=business_id, name=name, price=price, duration_minutes=duration_minutes)
    session.add(service)
    await session.commit()
    await session.refresh(service) 
    return service

async def get_services_catalog(business_id: int, session: AsyncSession):
    statement = select(Service).where(Service.business_id == business_id)
    services = await session.exec(statement)
    
    services_list = []
    for s in services:
        services_list.append(f"- **[ID: {s.id}]** {s.name} | {s.duration_minutes} mins | {s.price}€")
        
    list_format = "\n".join(services_list)

    if len(services_list) == 1:
        return f"""
        - DO NOT ask the client about the service they want to book, as there is only one service available. Use the ID: {services_list[0].split(':')[1].split(']')[0]} when calling 'get_available_slots'.
        """
    
    return f"""
    - This is our service catalog:
    <service_catalog>
    {list_format}
    </service_catalog>
    - If you don't know what service the client wants, ASK THEM.
    - Use the numerical ID from the catalog when calling the tool.
    """

async def delete_service(session: AsyncSession, id: int):
    service = await get_service_by_id(session=session, id=id)
    if service:
        await session.delete(service)
        await session.commit()
    return service

