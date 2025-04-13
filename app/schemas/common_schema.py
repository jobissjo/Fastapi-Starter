from typing import TypeVar, Generic, Optional, Literal
from pydantic import BaseModel
from app.models.enums import UserRole

T = TypeVar("T", bound=BaseModel)

class BaseResponse(BaseModel, Generic[T]):
    status: Literal["success", "error"]
    message: str
    data: Optional[T] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    role: UserRole

class RefreshTokenBody(BaseModel):
    refresh_token: str