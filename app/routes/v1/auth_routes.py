from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register():
    return {"message": "Register route"}

@router.post("/login")
def login():
    return {"message": "Login route"}   
