from fastapi import Depends
from app.core.security import verify_token_get_user
from app.models import User
from app.models.enums import UserRole
from app.utils.common import CustomException


async def only_admin(user: User = Depends(verify_token_get_user)):
    if user.is_superuser or user.role == UserRole.ADMIN:
        return user
    
    raise CustomException("You are not allowed to perform this action", status_code=403)

async def only_user(user: User = Depends(verify_token_get_user)):
    if user.role == UserRole.USER:
        return user
    
    raise CustomException("You are not allowed to perform this action", status_code=403)

async def any_user_role(user: User = Depends(verify_token_get_user)):
    return user