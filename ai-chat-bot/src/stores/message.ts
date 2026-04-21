import { ref, shallowRef, triggerRef, watch } from "vue";
import { defineStore } from "pinia";
import { getSessionDocuments } from "@/api/rag/rag";

export const useMessageStore = defineStore("message", () => {
  //   用户选择的会话ID
  const sessionId = ref<string>("");
  const documentIds = ref<number[]>([]);

  //   修改sessionId的函数
  function setSessionId(id: string) {
    sessionId.value = id;
  }

  //当sessionId变化了, 就根据sessionId获取documentIds,网络请求,使用getSessionDocuments
  watch(sessionId, async (newSessionId) => {
    if (newSessionId) {
      try {
        const res: any = await getSessionDocuments(newSessionId);
        // 从响应中提取documents数组中每个对象的id，组成新的数字数组
        const ids = res.documents?.map((doc: any) => doc.id) || [];
        setDocumentIds(ids);
      } catch (error: any) {
        // 如果是请求被取消的错误，静默处理（正常现象）
        if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
          console.log('前一个请求被取消，这是正常行为');
          return;
        }
        // 其他错误才需要处理
        console.error('获取文档列表失败:', error);
      }
    }
  });

  function setDocumentIds(ids: number[]) {
    documentIds.value = ids;
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
    const msgs = [
      ...message.value,
      { role: "assistant", content, isStreaming: true },
    ];
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
    documentIds,
    setDocumentIds,
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
