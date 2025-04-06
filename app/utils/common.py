from fastapi import status
from typing import Optional, Dict
import string
import random




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