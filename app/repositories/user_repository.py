from app.models.profile import Profile
from app.models.user import TempUserOTP, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.utils.common import generate_otp

class UserRepository:
    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> User:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
        query = select(User).options(joinedload(User.profile)).where(User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    

    @staticmethod
    async def get_user_profile_by_id(user_id: int, db: AsyncSession) -> User:
        query = select(Profile).where(Profile.user_id == user_id)
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
    
    @staticmethod
    async def update_profile(
        user_id: int,
        bio: str | None,
        profile_picture_url: str | None,
        db: AsyncSession,
    ) -> Profile:
        profile = await UserRepository.get_user_profile_by_id(user_id, db)

        if not profile:
            profile = Profile(user_id=user_id)

        if bio is not None:
            profile.bio = bio

        if profile_picture_url is not None:
            profile.profile_picture_url = profile_picture_url

        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile
    


