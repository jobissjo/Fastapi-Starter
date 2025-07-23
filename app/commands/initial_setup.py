import os
from pathlib import Path
import asyncio
import typer

def run():

    def initial_syn_operation():
        versions_folder = Path(__file__).parent.parent.parent / 'alembic' / 'versions'
        db_folder = Path(__file__).parent.parent / 'db'
        if not os.path.exists(versions_folder):
            print('Creating versions folder')
            os.makedirs(versions_folder)

        if not os.path.exists(db_folder):
            print('Creating db folder')
            os.makedirs(db_folder)

    async def create_initial_dev_setup():
        await asyncio.to_thread(initial_syn_operation)
        typer.echo(f"Initial Setup Completed Successfully")

    
    asyncio.run(create_initial_dev_setup())