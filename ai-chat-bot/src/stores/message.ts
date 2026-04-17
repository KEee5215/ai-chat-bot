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
    const msgs = [...message.value, { role: "user", content }];
    message.value = msgs;
    triggerRef(message);
    console.log("添加用户消息后，message.value:", message.value);
  }

  function removeUserMessage(index: number) {
    const msgs = message.value.filter((_, i) => i !== index);
    message.value = msgs;
    triggerRef(message);
  }

  function addAIMessage(content: string) {
    const msgs = [...message.value, { role: "assistant", content, isStreaming: true }];
    message.value = msgs;
    triggerRef(message);
    console.log("添加AI消息后，message.value:", message.value);
  }

  // 更新AI消息内容 - 原地修改，不触发响应式
  function updateAIMessageContent(index: number, content: string) {
    const msgs = [...message.value];
    if (msgs[index]) {
      msgs[index] = { ...msgs[index], content };
      message.value = msgs;
      triggerRef(message);
    }
  }

  function removeAIMessage(index: number) {
    const msgs = message.value.filter((_, i) => i !== index);
    message.value = msgs;
    triggerRef(message);
  }

  // 标记消息流式完成
  function markMessageComplete(index: number) {
    const msgs = [...message.value];
    if (msgs[index]) {
      msgs[index] = { ...msgs[index], isStreaming: false };
      message.value = msgs;
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
