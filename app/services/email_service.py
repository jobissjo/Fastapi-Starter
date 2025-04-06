from email.message import EmailMessage
from typing import Union, Optional
import aiosmtplib
import ssl
from app.models import User, EmailSetting
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger_config import logger
from app.utils import render_email_template


class EmailService:
    @staticmethod
    async def get_email_setting(
        db: AsyncSession,
        user: Optional[User] = None,
        use_admin_email: bool = False,
        
    ) -> EmailSetting:
        if use_admin_email:
            query = select(EmailSetting).where(
                EmailSetting.is_admin_mail.is_(True)
            )
        else:
            query = select(EmailSetting).where(
                EmailSetting.is_active.is_(True), EmailSetting.user_id == user.id
            )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def send_email(
        recipient: str,
        subject: str,
        template_name: str,
        template_data: dict[str, Union[str, int, bool]],
        user: Optional[User] = None,
        use_admin_email: bool = False,
        db: Optional[AsyncSession] = None,
    ):
        email_setting = await EmailService.get_email_setting(db, user, use_admin_email)
        email_body = await render_email_template(template_name, template_data)
        if not email_setting:
            user = user.first_name if user else "admin"
            logger.error(f"Email setting not found for user")
            return
        EMAIL_HOST_NAME = email_setting.host
        EMAIL_HOST_PORT = email_setting.port
        EMAIL_HOST_USERNAME = email_setting.email
        EMAIL_HOST_PASSWORD = email_setting.password
        message = EmailMessage()

        message["From"] = EMAIL_HOST_USERNAME
        message["To"] = recipient
        message["subject"] = subject
        message.set_content(email_body, subtype="html")

        context = ssl.create_default_context()

        await aiosmtplib.send(
            message,
            hostname=EMAIL_HOST_NAME,
            port=EMAIL_HOST_PORT,
            username=EMAIL_HOST_USERNAME,
            password=EMAIL_HOST_PASSWORD,
            start_tls=True,
            tls_context=context,
            # For compatibility with older versions of aiosmtplib
        )
