from datetime import datetime, timedelta, timezone
from app.schemas import user_schema
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, TempUserOTP
from sqlalchemy.future import select
from app.utils.common import CustomException, generate_otp
from app.core.security import create_access_token, hash_password, verify_password

# render_email_template, send_email
from app.services.email_service import EmailService


class UserService:
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession):
        query = select(User).where((User.email == email))

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        return existing_user

    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession):
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise CustomException(f"User with id {user_id} does not exist.", 404)

        return user

    @staticmethod
    async def register_user(user_data: user_schema.RegisterSchema, db: AsyncSession):
        
        otp = await TempUserOTPService.get_user_otp(user_data.email, db)
        if otp.otp != user_data.otp:
            raise CustomException("Invalid OTP", 400)

        existing_user = await UserService.get_user_by_email(user_data.email, db)

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
        query = select(User).where((User.email == user_data.email))

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            raise CustomException("email not exists", 400)
        correct_pwd = await verify_password(user_data.password, existing_user.password)
        if not correct_pwd:
            raise CustomException("Invalid credentials.", 401)
        access_token = await create_access_token({"user_id": existing_user.id})
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "role": existing_user.role,
        }

    @staticmethod
    async def verify_email(data: user_schema.EmailVerifySchema, db: AsyncSession):
        try:
            user = await UserService.get_user_by_email(data.email, db)
            if user and user.is_active:
                raise CustomException(message="Email already exists", status_code=400)

            user_otp = await TempUserOTPService.create_user_otp(data.email, db)
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


class TempUserOTPService:
    @staticmethod
    async def _get_otp_by_email(email: str, db: AsyncSession) -> TempUserOTP:
        query = select(TempUserOTP).where(TempUserOTP.email == email)
        result = await db.execute(query)
        otp = result.scalar_one_or_none()
        return otp

    @staticmethod
    async def get_user_otp(email: str, db: AsyncSession) -> TempUserOTP:
        otp = await TempUserOTPService._get_otp_by_email(email, db)
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
    async def create_user_otp(email: str, db: AsyncSession) -> TempUserOTP:
        otp = await generate_otp()
        existing_otp = await TempUserOTPService._get_otp_by_email(email, db)
        if existing_otp:
            await TempUserOTPService.delete_user_otp(email, db)
        user_otp = TempUserOTP(email=email, otp=otp)
        db.add(user_otp)
        await db.commit()
        await db.refresh(user_otp)
        return user_otp

    @staticmethod
    async def delete_user_otp(email: str, db: AsyncSession):
        query = select(TempUserOTP).where(TempUserOTP.email == email)
        result = await db.execute(query)
        otp = result.scalar_one_or_none()
        if otp is None:
            raise CustomException(message="Otp not found", status_code=400)
        await db.delete(otp)
        await db.commit()
        return {"message": "Otp deleted successfully"}
