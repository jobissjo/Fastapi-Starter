from fastapi import APIRouter, Depends
from app.schemas import BaseResponse, TokenResponse
from app.schemas.user_schema import (
    RegisterSchema,
    LoginEmailSchema,
    EmailVerifySchema
)
from fastapi.security import OAuth2PasswordRequestForm
from app.services import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import get_db
from typing import Annotated


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post('/verify-email')
async def verify_email(
    data: EmailVerifySchema, db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[None]:
    await UserService.verify_email(data, db)
    return BaseResponse(
        status="success", message="OTP sent successfully", data=None
    )


@router.post("/register")
async def register(
    data: RegisterSchema, db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[None]:
    current_user = await UserService.register_user(data, db)
    return BaseResponse(
        status="success", message="User registered successfully", data=None
    )


@router.post("/login")
async def login(
    data: LoginEmailSchema, db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[TokenResponse]:
    token_data = await UserService.login_user(data, db)
    return BaseResponse(
        status="success",
        message="User logged in successfully",
        data=TokenResponse(**token_data),
    )


@router.post("/token")
async def token(
    db: Annotated[AsyncSession, Depends(get_db)],
    data: OAuth2PasswordRequestForm = Depends(),
) -> BaseResponse[TokenResponse]:
    token_data = await UserService.login_user(
        LoginEmailSchema(email=data.username, password=data.password), db
    )
    return BaseResponse(
        status="success",
        message="User logged in successfully",
        data=TokenResponse(**token_data),
    )
