from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.common import CustomException


async def custom_exception_handler(_request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "data": exc.data,
            "status": "failed"
        },
    )