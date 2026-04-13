# app/schemas/response.py
from pydantic import BaseModel
from typing import Optional, Any


class ApiResponse(BaseModel):
    """统一响应模型"""
    code: int = 200
    data: Optional[Any] = None
    msg: str = "成功"
