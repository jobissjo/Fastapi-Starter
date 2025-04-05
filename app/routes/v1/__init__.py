from fastapi import APIRouter
from app.routes.v1 import auth_routes

router = APIRouter()
router.include_router(auth_routes.router)
