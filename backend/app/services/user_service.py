# app/services/user_service.py
class UserService:
    """用户服务"""

    @staticmethod
    def get_user(user_id: str) -> dict:
        """
        获取用户信息
        TODO: 从数据库查询用户信息
        """
        return {
            "user_id": user_id,
            "user_name": "John Doe"
        }
