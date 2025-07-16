from fastapi import FastAPI
from app.admin import setup_admin
from app.utils.common import CustomException
from app.middlewares import exception_handler
from app.routes.v1 import router as v1_router
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

app = FastAPI()

app.add_exception_handler(CustomException, exception_handler.custom_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handler.custom_validation_error_handler)
app.add_exception_handler(HTTPException, exception_handler.http_exception_handler)
app.add_exception_handler(Exception, exception_handler.unhandled_exception_handler)

setup_admin(app)

@app.get("/")
async def read_root():
 
    return {"Hello": "World"}


app.include_router(v1_router, prefix="/api/v1")
