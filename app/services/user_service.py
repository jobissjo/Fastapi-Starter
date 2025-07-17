from datetime import datetime, timedelta, timezone
from app.schemas import user_schema
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, TempUserOTP, Profile
from app.schemas.common_schema import RefreshTokenBody
from app.utils.common import CustomException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password, verify_refresh_token

# render_email_template, send_email
from app.services.common_service import  CommonService
from app.services.email_service import EmailService
from app.repositories import UserRepository
from app.core.logger_config import logger as default_logger
    
PROFILE_UPLOAD_FOLDER = 'profile'

class UserService:
    def __init__(self, email_service: EmailService, logger=None):
        self.email_service = email_service
        self.logger = logger or default_logger

    async def register_user(self, user_data: user_schema.RegisterSchema, db: AsyncSession):
        otp = await self.get_user_otp(user_data.email, db)
        if otp.otp != user_data.otp:
            raise CustomException("Invalid OTP", 400)

        existing_user = await UserRepository.get_user_by_email(user_data.email, db)

        if existing_user and existing_user.is_active:
            raise CustomException("A user with this username or email already exists.", 400)

        user_dict = user_data.model_dump(exclude={"otp"})
        hashed_password = await hash_password(user_dict["password"])

        if not existing_user:
            user_dict["password"] = hashed_password
            user = User(**user_dict)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

        elif not existing_user.is_active and existing_user.email == user_data.email:
            existing_user.password = hashed_password
            existing_user.role = user_data.role
            await db.commit()
            await db.refresh(existing_user)
            return existing_user

        raise CustomException("A user with this username already exists.", 400)

    async def login_user(self, user_data: user_schema.LoginEmailSchema, db: AsyncSession):
        existing_user = await UserRepository.get_user_by_email(user_data.email, db)
        if not existing_user:
            raise CustomException("email not exists", 400)

        if not await verify_password(user_data.password, existing_user.password):
            raise CustomException("Invalid credentials.", 401)

        access_token = await create_access_token({"user_id": existing_user.id})
        refresh_token = await create_refresh_token({"user_id": existing_user.id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "role": existing_user.role,
        }

    async def verify_email(self, data: user_schema.EmailVerifySchema, db: AsyncSession):
        user = await UserRepository.get_user_by_email(data.email, db)
        if user and user.is_active:
            raise CustomException("Email already exists", 400)

        user_otp = await UserRepository.create_user_otp(data.email, db)
        await self.email_service.send_email(
            recipient=data.email,
            subject="Verify Your Account",
            template_name="email/verify_account.html",
            template_data={"otp": user_otp.otp, "name": data.first_name},
            use_admin_email=True,
            db=db,
        )

    async def verify_email_otp(self, data: user_schema.EmailVerifyOtpSchema, db: AsyncSession):
        existing_user = await UserRepository.get_user_by_email(data.email, db)
        if existing_user and existing_user.is_active:
            raise CustomException("Email already exists", 400)

        user_otp = await self.get_user_otp(data.email, db)
        if user_otp.otp != data.otp:
            raise CustomException("Invalid OTP", 400)

    async def refresh_to_access_token(self, token_data: RefreshTokenBody, db: AsyncSession):
        payload = await verify_refresh_token(token_data.refresh_token)
        user_id = payload.get("user_id")

        if not user_id:
            raise CustomException("Invalid refresh token", 401)

        user = await UserRepository.get_user_by_id(user_id, db)
        if not user or not user.is_active:
            raise CustomException("User not found or inactive", 401)

        access_token = await create_access_token({"user_id": user.id})
        refresh_token = await create_refresh_token({"user_id": user.id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "role": user.role,
        }

    # Delegated from OTP service:
    async def get_user_otp(self, email: str, db: AsyncSession) -> TempUserOTP:
        otp = await UserRepository.get_otp_by_email(email, db)
        if otp is None:
            raise CustomException("OTP not found", 400)

        created_at = otp.created_at.replace(tzinfo=timezone.utc) if otp.created_at.tzinfo is None else otp.created_at
        if created_at < datetime.now(timezone.utc) - timedelta(minutes=5):
            await self.delete_user_otp(email, db)
            raise CustomException("OTP expired", 400)

        return otp

    async def delete_user_otp(self, email: str, db: AsyncSession):
        otp = await UserRepository.get_otp_by_email(email, db)
        if otp:
            await db.delete(otp)
            await db.commit()

    async def update_profile(
        self,
        user_id: int,
        data: user_schema.ProfileUpdateSchema,
        db: AsyncSession
    ) -> Profile:
        profile_picture_url = await CommonService.save_base64_file(data.profile_picture, PROFILE_UPLOAD_FOLDER ) if data.profile_picture else None
        
        return await UserRepository.update_profile(
            user_id=user_id,
            bio=data.bio,
            profile_picture_url=profile_picture_url,
            db=db
        )




class TempUserOTPService:
    @staticmethod
    async def get_user_otp(email: str, db: AsyncSession) -> TempUserOTP:
        otp = await UserRepository.get_otp_by_email(email, db)
        if otp is None:
            raise CustomException(message="Otp not found", status_code=400)
        created_at = otp.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if created_at < datetime.now(timezone.utc) - timedelta(minutes=5):
            await TempUserOTPService.delete_user_otp(email, db)
            raise CustomException(message="Otp expired", status_code=400)
        return otp

    @staticmethod
    async def delete_user_otp(email: str, db: AsyncSession):
        otp = await UserRepository.get_otp_by_email(email, db)
        if otp is None:
            raise CustomException(message="Otp not found", status_code=400)
        await db.delete(otp)
        await db.commit()
        return {"message": "Otp deleted successfully"}
