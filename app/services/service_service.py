from app.schemas.ai_tools import ServiceType
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

# Method created to help the ai, recognize which service is the client
async def get_services_catalog(business_id: int, session: Session):
    statement = select(Service).where(Service.business_id == business_id)
    services = await session.exec(statement)
    
    services_list = []
    for s in services:
        services_list.append(f"- **[ID: {s.id}]** {s.name} | {s.duration_minutes} mins | {s.price}€")
        
    list_format = "\n".join(services_list)

    if len(services) == 1:
        unique_service = services[0]
        return f"""
        - Este negocio ofrece un ÚNICO servicio genérico. 
        - NO le preguntes al cliente qué servicio quiere hacerse. Asume directamente que quieren una cita normal.
        - Cuando uses la herramienta 'check_availability_tool', pasa SIEMPRE el service_id: {unique_service.id}.
        """
    
    return f"""
    - Este es nuestro catálogo de servicios:
    <catalogo_servicios>
    {list_format}
    </catalogo_servicios>
    - Si no sabes qué servicio quiere el cliente, PREGÚNTALE.
    - Usa el ID numérico del catálogo al llamar a la herramienta.
    """
