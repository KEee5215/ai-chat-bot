# app/exceptions.py

class BusinessException(Exception):
    """业务异常"""
    def __init__(self, code: int = 400, message: str = "业务错误"):
        self.code = code
        self.message = message
        super().__init__(message)
