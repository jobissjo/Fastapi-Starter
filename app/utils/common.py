from fastapi import status
from typing import Optional, Dict
import string, random


def format_success_response(message:str, data:Optional[Dict]=None):
    return {"status": "success", "message": message, "data": data}


class CustomException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Optional[Dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.data = data

async def generate_otp(length: int = 6) -> str:

    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp