from passlib.context import CryptContext
import asyncio
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from typing import Optional, Annotated
from app.utils.common import CustomException
from datetime import datetime, timedelta, timezone
import jwt
from app.core.settings import setting
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import get_db
from app.models import User


pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(pwd_content.hash, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(pwd_content.verify, plain_password, hashed_password)


async def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=1080))
    to_encode.update({"exp": expire})
    return await asyncio.to_thread(
        jwt.encode, to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM
    )

async def verify_token_get_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
)->User:
    try:
        payload = await asyncio.to_thread(
            jwt.decode, token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise CustomException("Token is missing user id", status_code=401)
        
        from app.services import UserService
        return await UserService.get_user_by_id(user_id, db)
    
    except jwt.ExpiredSignatureError:
        raise CustomException("Token has expired", status_code=401)
    except jwt.PyJWTError as e:
        raise CustomException(f"Token is invalid: {e}", status_code=401)