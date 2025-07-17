from pydantic import BaseModel, Field

from app.models.enums import UserRole


class LoginEmailSchema(BaseModel):
    email: str
    password: str


class RegisterSchema(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    otp: str
    role: UserRole = Field(default=UserRole.USER)


class VerifyUserSchema(BaseModel):
    email: str
    otp: str


class EmailVerifySchema(BaseModel):
    first_name: str
    email: str


class EmailVerifyOtpSchema(BaseModel):
    otp: str
    email: str


class ProfileUpdateSchema(BaseModel):
    bio: str | None = Field(default=None, max_length=500)
    profile_picture: str | None = Field(
        default=None, description="Base64-encoded image string"
    )
