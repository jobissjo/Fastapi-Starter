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
    def __init__(self, logger_=None):
        self.logger = logger_ or logger

    async def get_email_setting(
        self,
        db: AsyncSession,
        user: Optional[User] = None,
        use_admin_email: bool = False,
    ) -> Optional[EmailSetting]:
        if use_admin_email:
            query = select(EmailSetting).where(
                EmailSetting.is_admin_mail.is_(True)
            )
        else:
            if not user:
                self.logger.error("User must be provided when not using admin email")
                return None
            query = select(EmailSetting).where(
                EmailSetting.is_active.is_(True), EmailSetting.user_id == user.id
            )

        result = await db.execute(query)
        return result.scalars().first()

    async def send_email(
        self,
        recipient: str,
        subject: str,
        template_name: str,
        template_data: dict[str, Union[str, int, bool]],
        user: Optional[User] = None,
        use_admin_email: bool = False,
        db: Optional[AsyncSession] = None,
    ):
        email_setting = await self.get_email_setting(db, user, use_admin_email)
        if not email_setting:
            who = user.first_name if user else "admin"
            self.logger.error(f"Email setting not found for {who}")
            return

        email_body = await render_email_template(template_name, template_data)

        message = EmailMessage()
        message["From"] = email_setting.email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(email_body, subtype="html")

        context = ssl.create_default_context()

        await aiosmtplib.send(
            message,
            hostname=email_setting.host,
            port=email_setting.port,
            username=email_setting.email,
            password=email_setting.password,
            start_tls=True,
            tls_context=context,
        )
