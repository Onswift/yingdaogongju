from typing import Optional, Any
from pydantic import BaseModel


class CommonResponse(BaseModel):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "message": message, "data": data}


def error_response(code: int, message: str) -> dict:
    """错误响应"""
    return {"code": code, "message": message, "data": None}


class ErrorCode:
    """错误码定义"""
    BAD_REQUEST = 1000
    UNAUTHORIZED = 1001
    NOT_FOUND = 1004
    INTERNAL_ERROR = 1005

    CARD_NOT_FOUND = 2000
    CARD_ALREADY_USED = 2001
    CARD_DISABLED = 2002
    CARD_EXPIRED = 2003

    LICENSE_NOT_FOUND = 3000
    LICENSE_EXPIRED = 3001
    LICENSE_BANNED = 3002
