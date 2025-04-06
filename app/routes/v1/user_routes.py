from fastapi import APIRouter, Depends
from app.core.security import verify_token_get_user
from app.models import User


router = APIRouter(prefix="/user", tags=["User"])

@router.get("/")
async def get_user(user:User=Depends(verify_token_get_user)):
    return user