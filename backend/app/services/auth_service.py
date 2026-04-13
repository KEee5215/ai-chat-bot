# app/services/auth_service.py
import time


class AuthService:
    """认证服务"""

    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        登录业务逻辑
        TODO: 这里应该验证用户名密码，查询数据库等
        """
        timestamp = int(time.time())
        return {
            "user_id": timestamp,
            "username": username,
            "token": "123456"  # TODO: 生成真实的 JWT token
        }
