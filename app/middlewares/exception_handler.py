from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.common import CustomException
from app.core.logger_config import logger
from starlette.exceptions import HTTPException as StarletteHTTPException


async def custom_exception_handler(request: Request, exc: CustomException):
    logger.error(f"{request.method} {request.url} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "data": exc.data,
            "status": "failed"
        },
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"{request.method} {request.url} - {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})