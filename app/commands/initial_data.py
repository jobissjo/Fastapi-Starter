from app.core.db_config import get_db
import asyncio
from app.models import EmailSetting, User
from app.core.settings import setting
import typer
from sqlalchemy import select


def run():
    async def create_initial_data():
        async for session in get_db():
            # Add your initial data creation logic here
            if not all([setting.EMAIL_TYPE, setting.EMAIL_HOST_NAME, setting.EMAIL_HOST_PORT,
                       setting.EMAIL_HOST_USERNAME, setting.EMAIL_HOST_PASSWORD]):
                typer.echo("Email settings are not configured properly")
                return
            
            query = select(User).where(User.is_superuser.is_(True))
            result = await session.execute(query)
            superuser = result.scalars().first()
            if not superuser:
                typer.echo("Superuser not found, first create a superuser")
                return

            email_setting = EmailSetting(
                email_type=setting.EMAIL_TYPE,
                host=setting.EMAIL_HOST_NAME,
                port=setting.EMAIL_HOST_PORT,
                email=setting.EMAIL_HOST_USERNAME,
                password=setting.EMAIL_HOST_PASSWORD,
                is_admin_mail=True,
                is_active=True,
                user_id=superuser.id,
            )
            session.add(email_setting)
            await session.commit()
            typer.echo(f"Email setting data created successfully for {superuser.email}({(superuser.first_name)})")
    
    asyncio.run(create_initial_data())
