from app.models.user import TempUserOTP, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.utils.common import generate_otp

class UserRepository:
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> User:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_otp_by_email(email: str, db: AsyncSession) -> TempUserOTP:
        query = select(TempUserOTP).where(TempUserOTP.email == email)
        result = await db.execute(query)
        otp = result.scalar_one_or_none()
        return otp
    
    @staticmethod
    async def create_user_otp(email: str, db: AsyncSession) -> TempUserOTP:
        otp = await generate_otp()
        existing_otp = await UserRepository.get_otp_by_email(email, db)
        if existing_otp:
            await db.delete(existing_otp)
            await db.flush()
        user_otp = TempUserOTP(email=email, otp=otp)
        db.add(user_otp)
        await db.commit()
        await db.refresh(user_otp)
        return user_otp
    


