from fastapi import FastAPI
from app.core.settings import setting

app = FastAPI()

@app.get("/")
async def read_root():
    print(setting.DATABASE_URL)
    print(setting.DATABASE_URL)
    return {"Hello": "World"}