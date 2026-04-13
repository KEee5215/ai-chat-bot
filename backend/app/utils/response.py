# app/utils/response.py
from typing import Optional, Any


def success_response(data: Any = None, msg: str = "成功") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "data": data,
        "msg": msg
    }


def error_response(code: int = 400, msg: str = "失败", data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "data": data,
        "msg": msg
    }
