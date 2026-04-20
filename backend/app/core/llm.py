# 大模型流式会话核心模块
import os
from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from app.settings import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


# 初始化 OpenAI 客户端(配置超时和连接池)
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,  # 支持自定义 API 地址(如国内代理)
    timeout=60.0,  # 请求超时时间(秒)
    max_retries=2  # 最大重试次数
)


async def chat_stream(
    messages: list,
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    流式调用 OpenAI 聊天接口
    
    Args:
        messages: 消息列表,格式为 [{"role": "user", "content": "..."}]
        model: 使用的模型名称
        temperature: 温度参数(0-2),控制随机性
        max_tokens: 最大生成 token 数
        **kwargs: 其他 OpenAI API 参数
    
    Yields:
        生成的文本片段
    
    Example:
        messages = [
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"}
        ]
        async for chunk in chat_stream(messages):
            print(chunk, end='', flush=True)
    """
    try:
        # 调用 OpenAI 流式接口
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,  # 启用流式输出
            **kwargs
        )
        
        # 逐块接收响应
        async for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:  # 只返回有内容的部分
                    yield delta.content
    
    except Exception as e:
        raise Exception(f"OpenAI API 调用失败: {str(e)}")


async def chat_complete(
    messages: list,
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> str:
    """
    非流式调用 OpenAI 聊天接口(一次性返回完整结果)
    
    Args:
        messages: 消息列表
        model: 使用的模型名称
        temperature: 温度参数
        max_tokens: 最大生成 token 数
        **kwargs: 其他参数
    
    Returns:
        完整的回复文本
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            **kwargs
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        raise Exception(f"OpenAI API 调用失败: {str(e)}")


# 辅助函数:构建消息列表
def build_messages(
    system_prompt: Optional[str] = None,
    user_message: Optional[str] = None,
    history: Optional[list] = None
) -> list:
    """
    构建标准的消息列表
    
    Args:
        system_prompt: 系统提示词
        user_message: 用户消息
        history: 历史对话记录
    
    Returns:
        格式化的消息列表
    """
    messages = []
    
    # 添加系统提示
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # 添加历史对话
    if history:
        messages.extend(history)
    
    # 添加当前用户消息
    if user_message:
        messages.append({"role": "user", "content": user_message})
    
    return messages


def get_llm(
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatOpenAI:
    """
    获取 LangChain 兼容的 LLM 实例
    
    Args:
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大 token 数
        **kwargs: 其他参数
    
    Returns:
        ChatOpenAI 实例
    """
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        **kwargs
    )