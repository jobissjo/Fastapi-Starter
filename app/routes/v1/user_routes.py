from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.db_config import get_db
from app.core.permissions import any_user_role
from app.models import User
from app.schemas.common_schema import BaseResponse
from app.schemas.user_schema import ProfileUpdateSchema
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import EmailService, UserService


router = APIRouter(prefix="/user", tags=["User"])

email_service = EmailService()
user_service = UserService(email_service=email_service)

@router.get("/",)
async def get_user(user:User=Depends(any_user_role)):
    return user

@router.patch("/", response_model=BaseResponse[None])
async def update_profile(
    data: ProfileUpdateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated = Depends(any_user_role),
):
    await user_service.update_profile(current_user.id, data, db)
    return BaseResponse(status="success", message="Profile updated successfully", data=None)