from typing import TypeVar, Generic, Optional, Literal
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T", bound=BaseModel)

class BaseResponse(GenericModel, Generic[T]):
    status: Literal["success", "error"]
    message: str
    data: Optional[T] = None