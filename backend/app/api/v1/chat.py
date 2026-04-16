import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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
async def stream_chat():
    """
    流式聊天接口 - 模拟 AI 回复
    
    返回 Server-Sent Events (SSE) 格式的流式数据
    """
    return StreamingResponse(
        simulate_stream(MARKDOWN_CONTENT, delay=0.03),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
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