from fastapi import FastAPI
from app.utils.common import CustomException
from app.middlewares import exception_handler
from app.routes.v1 import router as v1_router

app = FastAPI()

app.add_exception_handler(CustomException, exception_handler.custom_exception_handler)

@app.get("/")
async def read_root():
 
    return {"Hello": "World"}


app.include_router(v1_router, prefix="/api/v1")
