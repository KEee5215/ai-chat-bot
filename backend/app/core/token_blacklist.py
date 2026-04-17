"""
Token 黑名单管理

注意: 这是基于内存的实现,重启服务后黑名单会清空。
生产环境建议使用 Redis 或其他持久化存储。
"""
from datetime import datetime, timezone
from typing import Set


class TokenBlacklist:
    """Token 黑名单管理器(单例模式)"""
    
    _instance = None
    _blacklisted_tokens: Set[str] = set()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def add_token(self, token: str, expire_minutes: int = 30):
        """
        将 Token 加入黑名单
        
        Args:
            token: JWT Token
            expire_minutes: Token 剩余有效时间(分钟后自动清理)
        """
        self._blacklisted_tokens.add(token)
        
        # TODO: 生产环境应该设置定时任务,定期清理过期的黑名单记录
        # 例如使用 Redis 的 EXPIRE 命令
        
    def is_blacklisted(self, token: str) -> bool:
        """
        检查 Token 是否在黑名单中
        
        Args:
            token: JWT Token
        
        Returns:
            True 如果在黑名单中
        """
        return token in self._blacklisted_tokens
    
    def remove_token(self, token: str):
        """
        从黑名单中移除 Token
        
        Args:
            token: JWT Token
        """
        self._blacklisted_tokens.discard(token)
    
    def clear(self):
        """清空所有黑名单"""
        self._blacklisted_tokens.clear()
    
    @property
    def size(self) -> int:
        """获取黑名单大小"""
        return len(self._blacklisted_tokens)


# 全局实例
token_blacklist = TokenBlacklist()
