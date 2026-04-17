<template>
  <div class="flex flex-col h-full w-full">
    <div class="flex-1 overflow-y-auto py-32">
      <MessageItem
        v-for="(item, index) in message"
        :key="item.id"
        :content="item.content"
        :role="item.role"
      />
    </div>
    <div class="fixed bottom-0 left-0 right-0 bg-base-100">
      <div class="max-w-6xl mx-auto w-full h-32">
        <ChatInput></ChatInput>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { computed, nextTick, onMounted, ref, watch } from "vue";
import MessageItem from "../message/MessageItem.vue";

import { useMessageStore } from "@/stores/message";
import ChatInput from "./ChatInput.vue";
import { getMessage } from "@/api/chat/chat";
interface Message {
  id?: string;
  role: string;
  content: string;
  createdAt?: string;
}

const messageStore = useMessageStore();

const route = useRoute();

const message = computed(() => messageStore.message); // 使用 computed 保持响应式

const messageListRef = ref<HTMLDivElement>();

// 监听消息变化，自动滚动
watch(
  () => messageStore.message,
  async () => {
    await nextTick();
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
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
      let res: any = await getMessage(sessionId, 50);
      console.log("API返回的完整数据:", res);
      
      // 将获取到的消息设置到 store 中
      if (Array.isArray(res)) {
        console.log("使用 res 作为消息列表");
        messageStore.setMessages(res);
      } else if (res && res.data && Array.isArray(res.data)) {
        console.log("使用 res.data 作为消息列表");
        messageStore.setMessages(res.data);
      } else {
        console.warn("无法识别的消息数据结构:", res);
      }
      
      console.log("设置后的 messageStore.message:", messageStore.message);
    } catch (error) {
      console.error("获取消息失败:", error);
    }
  },
  { immediate: false }
);

onMounted(async () => {
  const sessionId = route.params.id as string;
  messageStore.setSessionId(sessionId);
  console.log("组件挂载，当前会话ID:", sessionId);
  
  try {
    let res: any = await getMessage(sessionId, 50);
    console.log("API返回的完整数据:", res);
    console.log("res.data:", res.data);
    console.log("res 是否为数组:", Array.isArray(res));
    console.log("res.data 是否为数组:", Array.isArray(res?.data));
    
    // 将获取到的消息设置到 store 中
    if (Array.isArray(res)) {
      // 如果 res 本身就是数组
      console.log("使用 res 作为消息列表");
      messageStore.setMessages(res);
    } else if (res && res.data && Array.isArray(res.data)) {
      // 如果 res.data 是数组
      console.log("使用 res.data 作为消息列表");
      messageStore.setMessages(res.data);
    } else {
      console.warn("无法识别的消息数据结构:", res);
    }
    
    console.log("设置后的 messageStore.message:", messageStore.message);
  } catch (error) {
    console.error("获取消息失败:", error);
  }
});
</script>
