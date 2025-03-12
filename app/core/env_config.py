from dotenv import load_dotenv
import os

load_dotenv()

ENV = os.getenv("ENV", "development")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLITE_PATH = os.path.join(BASE_DIR, "db", "dev.db")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{SQLITE_PATH}")

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-for-fastapi-application")