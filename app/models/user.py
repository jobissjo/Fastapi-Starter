from sqlalchemy import  Integer, String, Boolean, DateTime, func, Enum
from app.core.db_config import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.enums import UserRole

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    role : Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(),  onupdate=func.now())

    def __repr__(self) -> str:
        return f'<User(id={self.id}, email={self.email})>'
