from fastapi import APIRouter, Depends
from app.core.permissions import any_user_role
from app.models import User


router = APIRouter(prefix="/user", tags=["User"])

@router.get("/",)
async def get_user(user:User=Depends(any_user_role)):
    return user