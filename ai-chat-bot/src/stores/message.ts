import { ref, shallowRef, triggerRef } from "vue";
import { defineStore } from "pinia";

export const useMessageStore = defineStore("message", () => {
  //   用户选择的会话ID
  const sessionId = ref<string>("");

  //   修改sessionId的函数
  function setSessionId(id: string) {
    sessionId.value = id;
  }

  interface Message {
    id?: string;
    role: string;
    content: string;
    createdAt?: string;
    isStreaming?: boolean;
  }

  // 使用 shallowRef 避免深度监听性能问题
  const message = shallowRef<Message[]>([]);

  function addUserMessage(content: string) {
    const msgs = message.value;
    msgs.push({ role: "user", content });
    triggerRef(message);
  }

  function removeUserMessage(index: number) {
    message.value.splice(index, 1);
    triggerRef(message);
  }

  function addAIMessage(content: string) {
    const msgs = message.value;
    msgs.push({ role: "assistant", content, isStreaming: true });
    triggerRef(message);
  }

  // 更新AI消息内容 - 原地修改，不触发响应式
  function updateAIMessageContent(index: number, content: string) {
    const msgs = message.value;
    if (msgs[index]) {
      msgs[index].content = content;
      // 手动触发更新
      triggerRef(message);
    }
  }

  function removeAIMessage(index: number) {
    message.value.splice(index, 1);
    triggerRef(message);
  }

  // 标记消息流式完成
  function markMessageComplete(index: number) {
    const msgs = message.value;
    if (msgs[index]) {
      msgs[index].isStreaming = false;
      triggerRef(message);
    }
  }

  // 批量设置消息列表
  function setMessages(msgs: Message[]) {
    message.value = msgs;
    triggerRef(message);
  }

  return {
    message,
    addUserMessage,
    removeUserMessage,
    addAIMessage,
    removeAIMessage,
    updateAIMessageContent,
    markMessageComplete,
    setMessages,
    sessionId,
    setSessionId,
  };
});
