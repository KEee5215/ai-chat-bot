<template>
  <div
    class="flex gap-2 w-600 max-w-full px-4 py-4 items-center justify-center"
  >
    <textarea
      placeholder="type something ..."
      class="textarea flex-1 resize-none min-h-12 max-w-120"
      v-model="newMessage"
      :disabled="isLoading"
    ></textarea>
    <button
      :disabled="isNull || isLoading"
      class="btn btn-neutral btn-circle"
      @click="sendMessage"
    >
      <SendIcon v-if="!isLoading"></SendIcon>
      <span v-else class="loading loading-spinner loading-sm"></span>
    </button>
  </div>
</template>

<script setup lang="ts">
import SendIcon from "../icons/SendIcon.vue";
import { ref, watch } from "vue";
import { useMessageStore } from "@/stores/message";
import { useRoute } from "vue-router";
import { useRouter } from "vue-router";

const router = useRouter();

const route = useRoute();

const messageStore = useMessageStore();
const newMessage = ref<string>("");
const isLoading = ref(false);
let isNull = true;

watch(newMessage, (newValue) => {
  isNull = !newValue.trim();
});

async function sendMessage() {
  if (!newMessage.value.trim()) return;

  const userInput = newMessage.value;
  messageStore.addUserMessage(userInput);
  newMessage.value = "";
  isLoading.value = true;

  try {
    await fetchMessage(userInput);
  } catch (error) {
    console.error("Failed to fetch message:", error);
    messageStore.addAIMessage("抱歉，获取响应失败，请重试。");
  } finally {
    isLoading.value = false;
  }
}
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
              messageStore.updateAIMessageContent(aiMessageIndex, fullContent);
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
</script>

<style scoped></style>
