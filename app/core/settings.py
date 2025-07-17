from typing import Optional, List
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    ENV: str = "development"
    SECRET_KEY: str = "secret-key-for-fastapi-application"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    DATABASE_URL: Optional[str] = None

    SQLITE_PATH: Path = BASE_DIR /  "db" / "dev.db"

    MEDIA_ROOT: Path = BASE_DIR / "media"

    # SMTP settings
    EMAIL_TYPE: Optional[str] = None
    EMAIL_HOST_NAME: Optional[str] = None
    EMAIL_HOST_PORT: Optional[int] = None
    EMAIL_HOST_USERNAME: Optional[str] = None
    EMAIL_HOST_PASSWORD: Optional[str] = None

    CSRF_ORIGINS: List[str]  # noqa: F821

    def model_post_init(self, __context) -> None:
        if self.ENV == "development":
            object.__setattr__(self, "DATABASE_URL", f"sqlite+aiosqlite:///{self.SQLITE_PATH}")
        elif self.ENV == "production" and not self.DATABASE_URL:
            raise ValueError("❌ In production mode, DATABASE_URL must be set in the environment.")
        
    
        
        
    

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
setting = Settings()
