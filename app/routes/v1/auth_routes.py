from fastapi import APIRouter, Depends
from app.schemas import BaseResponse, TokenResponse
from app.schemas.common_schema import RefreshTokenBody
from app.schemas.user_schema import (
    EmailVerifyOtpSchema,
    RegisterSchema,
    LoginEmailSchema,
    EmailVerifySchema,
)
from fastapi.security import OAuth2PasswordRequestForm
from app.services import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import get_db
from typing import Annotated
from app.services import EmailService


router = APIRouter(prefix="/auth", tags=["Auth"])
email_service = EmailService()
user_service = UserService(email_service=email_service)


@router.post("/verify-email")
async def verify_email(
    data: EmailVerifySchema, db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[None]:
    await user_service.verify_email(data, db)
    return BaseResponse(status="success", message="OTP sent successfully", data=None)


@router.post("/verify-email-otp")
async def verify_email_otp(
    data: EmailVerifyOtpSchema, db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[None]:
    await user_service.verify_email_otp(data, db)
    return BaseResponse(
        status="success", message="Email verified successfully", data=None
    )


@router.post("/register")
async def register(
    data: RegisterSchema, db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[None]:
    _user = await user_service.register_user(data, db)
    return BaseResponse(
        status="success", message="User registered successfully", data=None
    )


@router.post("/login")
async def login(
    data: LoginEmailSchema, db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[TokenResponse]:
    token_data = await user_service.login_user(data, db)
    return BaseResponse(
        status="success",
        message="User logged in successfully",
        data=TokenResponse(**token_data),
    )


@router.post("/token")
async def token(
    db: Annotated[AsyncSession, Depends(get_db)],
    data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    token_data = await user_service.login_user(
        LoginEmailSchema(email=data.username, password=data.password), db
    )
    return TokenResponse(**token_data)


@router.post("/refresh")
async def refresh(
    db: Annotated[AsyncSession, Depends(get_db)],
    data: RefreshTokenBody,
) -> TokenResponse:
    token_data = await user_service.refresh_to_access_token(data, db)
    return TokenResponse(**token_data)
