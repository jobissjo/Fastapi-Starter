from sqlalchemy import Integer, String, Boolean, DateTime, func, Enum
from app.core.db_config import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.enums import UserRole
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

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={repr(self.email)})>"
