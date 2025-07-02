from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import asyncio

template_path = Path(__file__).parent.parent / 'templates'
environment = Environment(loader=FileSystemLoader(template_path))

async def render_email_template(template_name:str, payload_data:dict):
    template = environment.get_template(template_name)
    return await asyncio.to_thread(template.render, **payload_data)


