from pydantic import BaseModel
from typing import Optional, Any


class CommonResponse(BaseModel):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
