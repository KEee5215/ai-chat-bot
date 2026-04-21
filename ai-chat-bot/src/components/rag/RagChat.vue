<template>
  <div class="flex flex-col h-full w-full">
    <div ref="messageListRef" class="flex-1 overflow-y-auto py-32">
      <MessageItem
        v-for="(item, index) in message"
        :key="item.id || index"
        :content="item.content"
        :role="item.role"
      />
    </div>
    <div class="fixed bottom-0 left-0 right-0 bg-base-100">
      <div class="max-w-6xl mx-auto w-full h-32">
        <RagChatInput></RagChatInput>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { computed, nextTick, onMounted, ref, watch } from "vue";
import MessageItem from "../message/MessageItem.vue";

import { useMessageStore } from "@/stores/message";

import { getSessionMessages } from "@/api/rag/rag";

import RagChatInput from "./RagChatInput.vue";
interface Message {
  id?: string;
  role: string;
  content: string;
  createdAt?: string;
}

const messageStore = useMessageStore();

// 将历史消息转换为 store 需要的格式
function convertHistoryToMessages(history: any[]) {
  const messages: Message[] = [];
  
  // 反转数组，使最旧的消息在前，最新的消息在后
  const reversedHistory = [...history].reverse();
  
  reversedHistory.forEach((item) => {
    // 添加用户消息
    messages.push({
      id: `user-${item.id}`,
      role: "user",
      content: item.user_question,
    });
    
    // 添加 AI 回复
    messages.push({
      id: `ai-${item.id}`,
      role: "assistant",
      content: item.ai_answer,
    });
  });
  
  return messages;
}

const route = useRoute();

const message = computed(() => messageStore.message); // 使用 computed 保持响应式

const messageListRef = ref<HTMLDivElement>();

// 监听消息变化，自动滚动
watch(
  () => messageStore.message,
  (newVal, oldVal) => {
    console.log("消息列表变化:", {
      旧长度: oldVal?.length,
      新长度: newVal.length,
      最新消息: newVal[newVal.length - 1],
    });
    nextTick(() => {
      if (messageListRef.value) {
        messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
      }
    });
  },
  { deep: true },
);

// 监听路由参数变化，重新加载消息
watch(
  () => route.params.id,
  async (newSessionId) => {
    if (!newSessionId) return;

    const sessionId = newSessionId as string;
    messageStore.setSessionId(sessionId);
    console.log("路由变化，当前会话ID:", sessionId);

    try {
      const res: any = await getSessionMessages(sessionId, 1, 50);
      console.log("API返回的完整数据:", res);

      // 根据返回结构提取 history 数组
      if (res && res.history && Array.isArray(res.history)) {
        console.log("使用 res.history 作为历史消息");
        const messages = convertHistoryToMessages(res.history);
        messageStore.setMessages(messages);
      } else {
        console.warn("无法识别的消息数据结构:", res);
      }

      console.log("设置后的 messageStore.message:", messageStore.message);
    } catch (error) {
      console.error("获取消息失败:", error);
    }
  },
  { immediate: false },
);

onMounted(async () => {
  const sessionId = route.params.id as string;
  messageStore.setSessionId(sessionId);
  console.log("组件挂载，当前会话ID:", sessionId);

  try {
    const res: any = await getSessionMessages(sessionId, 1, 50);
    console.log("API返回的完整数据:", res);

    // 根据返回结构提取 history 数组
    if (res && res.history && Array.isArray(res.history)) {
      console.log("使用 res.history 作为历史消息");
      const messages = convertHistoryToMessages(res.history);
      messageStore.setMessages(messages);
    } else {
      console.warn("无法识别的消息数据结构:", res);
    }

    console.log("设置后的 messageStore.message:", messageStore.message);
  } catch (error) {
    console.error("获取消息失败:", error);
  }
});
</script>
