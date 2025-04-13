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
from app.repositories import UserRepository


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
    to_encode.update({"exp": expire, "token_type": "access"})
    return await asyncio.to_thread(
        jwt.encode, to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM
    )


async def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({
        "exp": expire,
        "token_type": "refresh"  # you can differentiate token types if needed
    })
    
    return await asyncio.to_thread(
        jwt.encode, to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM
    )

async def verify_refresh_token(token: str) -> dict:
    try:
        payload = await asyncio.to_thread(
            jwt.decode, token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM]
        )
        if payload.get("token_type") != "refresh":
            raise CustomException("Invalid token type", status_code=401)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise CustomException("Token is missing user id", status_code=401)
        return payload
    except jwt.ExpiredSignatureError:
        raise CustomException("Token has expired", status_code=401)
    except jwt.PyJWTError as e:
        raise CustomException(f"Token is invalid: {e}", status_code=401)


async def verify_token_get_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
)->User:
    try:
        payload = await asyncio.to_thread(
            jwt.decode, token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM]
        )
        if payload.get("token_type") != "access":
            raise CustomException("Invalid token type", status_code=401)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise CustomException("Token is missing user id", status_code=401)
        
        return await UserRepository.get_user_by_id(user_id, db)
    
    except jwt.ExpiredSignatureError:
        raise CustomException("Token has expired", status_code=401)
    except jwt.PyJWTError as e:
        raise CustomException(f"Token is invalid: {e}", status_code=401)