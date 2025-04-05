from email.message import EmailMessage
import aiosmtplib
import ssl
from app.models import User, EmailSetting
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger_config import logger


class EmailService:
    @staticmethod
    async def get_email_setting(
        user: User, db: AsyncSession,
        use_admin_email: bool = False,
        
    ) -> EmailSetting:
        if use_admin_email:
            query = select(EmailSetting).where(
                EmailSetting.is_admin_mail.is_(True), EmailSetting.is_active.is_(True)
            )
        else:
            query = select(EmailSetting).where(
                EmailSetting.is_active.is_(True), EmailSetting.user_id == user.id
            )
        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def send_email(
        user: User,
        recipient: str,
        subject: str,
        email_body: str,
        use_admin_email: bool = False,
    ):
        email_setting = await EmailService.get_email_setting(user, use_admin_email)
        if not email_setting:
            logger.error(f"Email setting not found for user {user.id}")
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
