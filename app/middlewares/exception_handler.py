from fastapi import Request
from fastapi.responses import JSONResponse

from app.utils.common import CustomException
from app.core.logger_config import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from fastapi.encoders import jsonable_encoder


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


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"{request.method} {request.url} - {exc} - unhandled exception")
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})




def custom_validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        errors.append({
            "fieldName": field,
            "errors": [err["msg"]]
        })

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "message": "Validation failed",
            "detail": errors,
            "error_type": "validation_error",
            "data": None
        }),
    )
