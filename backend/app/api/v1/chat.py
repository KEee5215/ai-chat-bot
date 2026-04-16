import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id, get_current_user
from app.dependencies import get_session
from app.core.llm import chat_stream, build_messages

from app.repository.chat_repo import ChatSessionRepository, ChatMessageRepository
from app.schemas.chat import ChatIn, SessionIn

router = APIRouter(prefix="/chat", tags=["聊天"])


# 模拟的 Markdown 文档内容
MARKDOWN_CONTENT = """# FastAPI 异步编程指南

## 简介

FastAPI 是一个现代、快速(高性能)的 Web 框架,用于构建 API。

### 主要特性

- **快速**: 非常高的性能,与 NodeJS 和 Go 相当
- **快速编码**: 提高功能开发速度约 200% 至 300%
- **更少 bug**: 减少约 40% 的人为错误
- **直观**: 强大的编辑器支持,自动补全无处不在
- **简易**: 旨在易于使用和学习

## 异步编程基础

### 什么是异步?

异步编程允许程序在等待某些操作完成时继续执行其他任务。

```python
async def fetch_data():
    # 模拟异步操作
    await asyncio.sleep(1)
    return {"data": "result"}
```

### async/await 语法

- `async def`: 定义异步函数
- `await`: 等待异步操作完成

## 最佳实践

1. **使用异步数据库驱动**
2. **避免阻塞操作**
3. **合理使用并发**

## 总结

异步编程可以显著提高应用性能,但需要正确理解和使用。

> 记住: 不是所有场景都需要异步!
"""


async def simulate_stream(content: str, delay: float = 0.05):
    """
    模拟流式输出,逐个字符发送
    
    Args:
        content: 要发送的内容
        delay: 每个字符之间的延迟(秒)
    """
    for char in content:
        # 模拟 AI 生成的延迟
        await asyncio.sleep(delay)
        # 按照 SSE (Server-Sent Events) 格式发送
        yield f"data: {json.dumps({'content': char}, ensure_ascii=False)}\n\n"
    
    # 发送结束标记
    yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def stream_chat(
    request_body: ChatIn,
    session: AsyncSession = Depends(get_session),
        user_id: int = Depends(get_current_user_id)
):
    """
    流式聊天接口 - 调用 OpenAI API
    
    Request Body:
    {
        "message": "用户消息",
        "session_id": 1,  // 可选,会话ID,不提供则创建新会话
        "system_prompt": "可选的系统提示"
    }
    """

    user_message = request_body.message
    session_id = request_body.session_id

    if not user_message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # 如果没有提供 session_id,拒绝
    if not session_id:
        raise HTTPException(status_code=400, detail="会话ID不能为空")
    else:
        # 验证会话归属
        session_repo = ChatSessionRepository(session)
        chat_session = await session_repo.get_session_by_id(session_id, user_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    
    # 保存用户消息
    message_repo = ChatMessageRepository(session)
    await message_repo.add_message(
        session_id=session_id,
        role="user",
        content=user_message
    )
    
    # 获取历史对话(最近20条)
    history_messages = await message_repo.get_last_n_messages(
        session_id=session_id,
        user_id=user_id,
        n=20
    )
    
    # 构建消息列表(不包含刚添加的用户消息,因为会重复)
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages[:-1]  # 排除最后一条(刚添加的用户消息)
    ]
    
    messages = build_messages(
        user_message=user_message,
        history=history
    )
    
    async def generate():
        """生成流式响应"""
        assistant_response = ""
        try:
            async for chunk in chat_stream(messages):
                assistant_response += chunk
                # SSE 格式
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)  # 让出控制权
            
            # 保存 AI 回复
            await message_repo.add_message(
                session_id=session_id,
                role="assistant",
                content=assistant_response
            )
            
        except Exception as e:
            error_msg = str(e)
            yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
        finally:
            # 发送结束标记
            yield f"data: {json.dumps({'done': True, 'session_id': session_id}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/stream/demo")
async def stream_demo():
    """
    GET 方式的流式演示接口(方便浏览器测试)
    """
    return StreamingResponse(
        simulate_stream(MARKDOWN_CONTENT, delay=0.02),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ==================== 会话管理接口 ====================
# 新增会话
@router.post("/sessions")
async def create_session(
    request_body: SessionIn,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    session_repo = ChatSessionRepository(session)
    session_id = await session_repo.create_session(
        user_id=user_id,
        title=request_body.title
    )
    return {
        "code": 200,
        "data": {
            "session_id": session_id
        },
        "msg": "成功"
    }


@router.get("/sessions")
async def get_user_sessions(
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的会话列表(分页)
    
    Query Parameters:
        page: 页码(从1开始)
        page_size: 每页数量
    """
    user_id = current_user["user_id"]
    session_repo = ChatSessionRepository(session)
    sessions = await session_repo.get_user_sessions(
        user_id=user_id,
        page=page,
        page_size=page_size
    )
    
    return {
        "code": 200,
        "data": [
            {
                "id": s.id,
                "title": s.title,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat()
            }
            for s in sessions
        ],
        "msg": "成功"
    }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    获取指定会话的对话历史
    
    Path Parameters:
        session_id: 会话ID
    
    Query Parameters:
        limit: 返回消息数量限制
    """
    user_id = current_user["user_id"]
    message_repo = ChatMessageRepository(session)
    messages = await message_repo.get_session_messages(
        session_id=session_id,
        user_id=user_id,
        limit=limit
    )
    
    return {
        "code": 200,
        "data": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ],
        "msg": "成功"
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    删除会话(软删除)
    
    Path Parameters:
        session_id: 会话ID
    """
    user_id = current_user["user_id"]
    session_repo = ChatSessionRepository(session)
    success = await session_repo.delete_session(
        session_id=session_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在或无权删除")
    
    return {
        "code": 200,
        "data": None,
        "msg": "删除成功"
    }


@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: int,
    request_body: dict,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    更新会话标题
    
    Path Parameters:
        session_id: 会话ID
    
    Request Body:
        {
            "title": "新标题"
        }
    """
    user_id = current_user["user_id"]
    title = request_body.get("title", "")
    
    if not title:
        raise HTTPException(status_code=400, detail="标题不能为空")
    
    session_repo = ChatSessionRepository(session)
    success = await session_repo.update_session_title(
        session_id=session_id,
        user_id=user_id,
        title=title
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在或无权修改")
    
    return {
        "code": 200,
        "data": None,
        "msg": "更新成功"
    }