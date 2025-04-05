from sqlalchemy import Integer, String, Boolean, DateTime, func, Enum
from app.core.db_config import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from app.models.enums import UserRole, EmailType
from reprlib import repr
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.profile import Profile

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)
    email_settings: Mapped["EmailSetting"] = relationship(
        "EmailSetting", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={repr(self.email)})>"


class TempUserOTP(Base):
    __tablename__ = "temp_user_otp"
    __table_args__ = {"sqlite_autoincrement": True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    otp: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<TempUserOTP(id={self.id}, email={repr(self.email)})>"
    

class EmailSetting(Base):
    __tablename__ = "email_settings"
    __table_args__ = {"sqlite_autoincrement": True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email_type: Mapped[EmailType] = mapped_column(
        Enum(EmailType), default=EmailType.SMTP, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    host: Mapped[str] = mapped_column(String, nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin_mail: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), index=True
    )

    user: Mapped["User"] = relationship("User", backref="email_settings")

    def __repr__(self) -> str:
        return f"<EmailSetting(id={self.id}, email={repr(self.email)})>"
