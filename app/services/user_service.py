from datetime import datetime, timedelta, timezone
from app.schemas import user_schema
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, TempUserOTP
from sqlalchemy.future import select
from app.schemas.common_schema import RefreshTokenBody
from app.utils.common import CustomException, generate_otp
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password, verify_refresh_token

# render_email_template, send_email
from app.services.email_service import EmailService
from app.repositories import UserRepository


class UserService:


    @staticmethod
    async def register_user(user_data: user_schema.RegisterSchema, db: AsyncSession):
        
        otp = await TempUserOTPService.get_user_otp(user_data.email, db)
        if otp.otp != user_data.otp:
            raise CustomException("Invalid OTP", 400)

        existing_user = await UserRepository.get_user_by_email(user_data.email, db)

        if existing_user and existing_user.is_active:
            raise CustomException(
                "A user with this username or email already exists.", 400
            )
        user_data = user_data.model_dump().copy()
        user_data.pop("otp")
        hashed_password = await hash_password(user_data["password"])
        if not existing_user:
            user_data["password"] = hashed_password
            user = User(**user_data)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        elif not existing_user.is_active and existing_user.email == user_data["email"]:
            existing_user.password = hashed_password
            existing_user.role = user_data["role"]
            await db.commit()
            await db.refresh(existing_user)
            return existing_user
        else:
            raise CustomException("A user with this username already exists.", 400)

    @staticmethod
    async def login_user(user_data: user_schema.LoginEmailSchema, db: AsyncSession):
        existing_user = await UserRepository.get_user_by_email(user_data.email, db)
        if not existing_user:
            raise CustomException("email not exists", 400)
        correct_pwd = await verify_password(user_data.password, existing_user.password)
        if not correct_pwd:
            raise CustomException("Invalid credentials.", 401)
        access_token = await create_access_token({"user_id": existing_user.id})
        refresh_token = await create_refresh_token({"user_id": existing_user.id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "role": existing_user.role,
        }

    @staticmethod
    async def verify_email(data: user_schema.EmailVerifySchema, db: AsyncSession):
        try:
            user = await UserRepository.get_user_by_email(data.email, db)
            if user and user.is_active:
                raise CustomException(message="Email already exists", status_code=400)
        
            user_otp = await UserRepository.create_user_otp(data.email, db)
            await EmailService.send_email(
                data.email,
                "Verify Your Account",
                "verify_account.html",
                {"otp": user_otp.otp, "name": data.first_name},
                use_admin_email=True,
                db=db,
            )
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(message=str(e), status_code=400)
        
    @staticmethod
    async def verify_email_otp(
        data: user_schema.EmailVerifyOtpSchema, db: AsyncSession
    ):
        existing_user = await UserRepository.get_user_by_email(data.email, db)
        if existing_user and existing_user.is_active:
            raise CustomException(message="Email already exists", status_code=400)
        user_otp = await TempUserOTPService.get_user_otp(data.email, db)
        if user_otp.otp != data.otp:
            raise CustomException(message="Invalid OTP", status_code=400)
        
    
    @staticmethod
    async def refresh_to_access_token(token_data: RefreshTokenBody, db: AsyncSession):
        payload = await verify_refresh_token(token_data.refresh_token)
        user_id = payload.get("user_id")
        if not user_id:
            raise CustomException("Invalid refresh token", 401)
        # check if user exists
        user = await UserRepository.get_user_by_id(user_id, db)
        if user is None:
            raise CustomException("User not found", 401)
        if not user.is_active:
            raise CustomException("User is not active", 401)
        # create access token
        access_token = await create_access_token({"user_id": user.id})
        refresh_token = await create_refresh_token({"user_id": user.id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "role": user.role,
        }
        
        
        



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
