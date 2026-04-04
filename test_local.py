import asyncio
from sqlmodel import select
from datetime import date
from app.database import engine # Ajusta esto a donde tengas tu engine
from sqlmodel.ext.asyncio.session import AsyncSession
# Importa la función que quieres probar
from app.models import Service
from app.services.appointment_service import get_available_slots, create_appointment

async def probar_mi_codigo():
    # 1. Abrimos una sesión real con la base de datos
    async with AsyncSession(engine) as session:
        
        print("⏳ Ejecutando la función...")
        
        # 2. Llamamos a tu método pasándole la sesión y los parámetros
        consulta_servicio = select(Service).where(Service.name == "Corte de Pelo")
        resultado = await session.exec(consulta_servicio)
        servicio_real = resultado.first()
        
        await get_available_slots(date(2026, 4, 3), session, 1, servicio_real.id)

if __name__ == "__main__":
    # Como tu método es asíncrono, necesitamos encender el motor de Python
    asyncio.run(probar_mi_codigo())