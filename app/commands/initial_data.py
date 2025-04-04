from app.core.db_config import get_db
import asyncio

def run():
    async def create_initial_data():
        async for _session in get_db():
            # Add your initial data creation logic here
            pass
    
    asyncio.run(create_initial_data())
