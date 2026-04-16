from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatSession, ChatMessage


class ChatSessionRepository:
    """聊天会话数据访问层"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, user_id: int, title: str = "新对话") -> ChatSession:
        """
        创建新的聊天会话
        
        Args:
            user_id: 用户ID
            title: 会话标题
        
        Returns:
            创建的会话对象
        """
        session = ChatSession(
            user_id=user_id,
            title=title,
            is_deleted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.session.add(session)
        await self.session.flush()
        return session

    async def get_session_by_id(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        """
        根据ID获取会话(验证用户权限)
        
        Args:
            session_id: 会话ID
            user_id: 用户ID(用于权限验证)
        
        Returns:
            会话对象或None
        """
        stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_sessions(self, user_id: int, page: int = 1, page_size: int = 20) -> List[ChatSession]:
        """
        获取用户的所有会话(分页)
        
        Args:
            user_id: 用户ID
            page: 页码(从1开始)
            page_size: 每页数量
        
        Returns:
            会话列表
        """
        offset = (page - 1) * page_size
        stmt = (
            select(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.is_deleted == False
            )
            .order_by(ChatSession.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_session_title(self, session_id: int, user_id: int, title: str) -> bool:
        """
        更新会话标题
        
        Args:
            session_id: 会话ID
            user_id: 用户ID(用于权限验证)
            title: 新标题
        
        Returns:
            是否更新成功
        """
        stmt = (
            update(ChatSession)
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
            .values(title=title, updated_at=datetime.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        """
        软删除会话(标记为已删除)
        
        Args:
            session_id: 会话ID
            user_id: 用户ID(用于权限验证)
        
        Returns:
            是否删除成功
        """
        stmt = (
            update(ChatSession)
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
            .values(is_deleted=True, updated_at=datetime.now())
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def hard_delete_session(self, session_id: int, user_id: int) -> bool:
        """
        硬删除会话及所有消息(谨慎使用)
        
        Args:
            session_id: 会话ID
            user_id: 用户ID(用于权限验证)
        
        Returns:
            是否删除成功
        """
        # 先删除该会话的所有消息
        await self.session.execute(
            delete(ChatMessage).where(ChatMessage.session_id == session_id)
        )
        
        # 再删除会话
        stmt = delete(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class ChatMessageRepository:
    """聊天消息数据访问层"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_message(self, session_id: int, role: str, content: str, token_count: int = 0) -> ChatMessage:
        """
        添加消息到会话
        
        Args:
            session_id: 会话ID
            role: 角色 ('user', 'assistant', 'system')
            content: 消息内容
            token_count: token数量
        
        Returns:
            创建的消息对象
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            token_count=token_count,
            created_at=datetime.now()
        )
        self.session.add(message)
        await self.session.flush()
        
        # 更新会话的更新时间
        await self.session.execute(
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(updated_at=datetime.now())
        )
        
        return message

    async def add_messages_batch(self, session_id: int, messages: List[dict]) -> List[ChatMessage]:
        """
        批量添加消息
        
        Args:
            session_id: 会话ID
            messages: 消息列表,格式为 [{"role": "user", "content": "..."}, ...]
        
        Returns:
            创建的消息对象列表
        """
        created_messages = []
        for msg_data in messages:
            message = await self.add_message(
                session_id=session_id,
                role=msg_data["role"],
                content=msg_data["content"],
                token_count=msg_data.get("token_count", 0)
            )
            created_messages.append(message)
        
        return created_messages

    async def get_session_messages(self, session_id: int, user_id: int, limit: int = 100) -> List[ChatMessage]:
        """
        获取会话的对话历史
        
        Args:
            session_id: 会话ID
            user_id: 用户ID(用于权限验证)
            limit: 返回消息数量限制
        
        Returns:
            消息列表(按时间正序)
        """
        # 先验证会话归属
        session_stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False
        )
        session_result = await self.session.execute(session_stmt)
        if not session_result.scalars().first():
            return []
        
        # 查询消息
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_last_n_messages(self, session_id: int, user_id: int, n: int = 10) -> List[ChatMessage]:
        """
        获取最近的N条消息(用于上下文)
        
        Args:
            session_id: 会话ID
            user_id: 用户ID(用于权限验证)
            n: 消息数量
        
        Returns:
            消息列表(按时间正序)
        """
        # 先验证会话归属
        session_stmt = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False
        )
        session_result = await self.session.execute(session_stmt)
        if not session_result.scalars().first():
            return []
        
        # 查询最近N条消息
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(n)
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()
        
        # 反转使其按时间正序
        return list(reversed(messages))

    async def delete_message(self, message_id: int, session_id: int) -> bool:
        """
        删除单条消息
        
        Args:
            message_id: 消息ID
            session_id: 会话ID(用于验证)
        
        Returns:
            是否删除成功
        """
        stmt = delete(ChatMessage).where(
            ChatMessage.id == message_id,
            ChatMessage.session_id == session_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def clear_session_messages(self, session_id: int) -> int:
        """
        清空会话的所有消息
        
        Args:
            session_id: 会话ID
        
        Returns:
            删除的消息数量
        """
        stmt = delete(ChatMessage).where(ChatMessage.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_message_count(self, session_id: int) -> int:
        """
        获取会话的消息总数
        
        Args:
            session_id: 会话ID
        
        Returns:
            消息数量
        """
        from sqlalchemy import func
        stmt = select(func.count(ChatMessage.id)).where(
            ChatMessage.session_id == session_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
