import { useMessageStore } from "@/stores/message";

/**
 * 组合式函数：处理消息发送和流式响应
 * @returns 返回sendMessage函数
 */
export function useSendMessageStream() {
  const messageStore = useMessageStore();

  /**
   * 发送消息的主函数
   * @param message - 用户输入的消息
   */
  async function sendMessage(message: string) {
    if (!message.trim()) return;

    const userInput = message;
    console.log("准备发送消息:", userInput);
    console.log(
      "发送前 messageStore.message 长度:",
      messageStore.message.length,
    );

    messageStore.addUserMessage(userInput);
    console.log(
      "添加用户消息后 messageStore.message 长度:",
      messageStore.message.length,
    );
    console.log("当前消息列表:", messageStore.message);

    try {
      await fetchMessage(userInput);
    } catch (error) {
      console.error("Failed to fetch message:", error);
      messageStore.addAIMessage("抱歉，获取响应失败，请重试。");
    }
  }

  /**
   * 获取AI响应的流式数据
   * @param message - 用户消息
   */
  async function fetchMessage(message: string) {
    const token = localStorage.getItem("token");

    if (!token) {
      throw new Error("未授权：请重新登录");
    }

    const sessionId = messageStore.sessionId;
    if (!sessionId) {
      throw new Error("未选择会话");
    }

    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      if (response.status === 400) {
        const errorData = await response.json().catch(() => ({}));
        console.error("请求错误:", errorData);
        throw new Error(`请求数据有误`);
      }
      if (response.status === 401) {
        throw new Error("授权过期，请重新登录");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("Response body is not readable");

    const decoder = new TextDecoder();
    let fullContent = "";
    let aiMessageIndex = -1;

    messageStore.addAIMessage("");
    aiMessageIndex = messageStore.message.length - 1;

    try {
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log("✅ 流式响应完成，总字数:", fullContent.length);
          break;
        }

        const text = decoder.decode(value, { stream: true });
        buffer += text;

        // 按换行符分割
        const lines = buffer.split("\n");

        // 保留最后一行（可能不完整）
        buffer = lines.pop() || "";

        for (let line of lines) {
          console.log("📨 收到行:", line); // 调试日志

          if (line.startsWith("data: ")) {
            try {
              const jsonStr = line.slice(6);
              console.log("📦 JSON:", jsonStr); // 调试日志

              const data = JSON.parse(jsonStr);
              if (data.content) {
                fullContent += data.content;
                console.log("📝 更新内容:", fullContent); // 调试日志
                messageStore.updateAIMessageContent(
                  aiMessageIndex,
                  fullContent,
                );
              }
            } catch (e) {
              console.debug("❌ 解析 SSE 数据失败:", line);
            }
          }
        }
      }

      // 处理缓存中残留的数据
      if (buffer.trim().startsWith("data: ")) {
        try {
          const data = JSON.parse(buffer.slice(6));
          if (data.content) {
            fullContent += data.content;
            messageStore.updateAIMessageContent(aiMessageIndex, fullContent);
          }
        } catch (e) {
          console.debug("解析最后一行失败");
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  return {
    sendMessage,
  };
}
