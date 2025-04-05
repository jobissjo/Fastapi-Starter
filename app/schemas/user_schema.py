
from pydantic import BaseModel, Field

from app.models.enums import UserRole


class LoginUsernameSchema(BaseModel):
    username: str
    password: str

class LoginEmailSchema(BaseModel):
    email: str
    password: str

class RegisterSchema(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: UserRole = Field(default=UserRole.USER)