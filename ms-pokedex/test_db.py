import asyncio
from sqlalchemy import text
from app.core.database import engine


async def main():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("¡Conexión a PostgreSQL OK!", result.scalar())


asyncio.run(main())