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
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("Response body is not readable");

  const decoder = new TextDecoder();
  let fullContent = "";
  let aiMessageIndex = -1;

  // 先添加一个空的 AI 消息
  messageStore.addAIMessage("");
  aiMessageIndex = messageStore.message.length - 1;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      const lines = text.split("\n");

      for (let line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.content) {
              fullContent += data.content;
              // 实时更新 UI
              messageStore.updateAIMessageContent(aiMessageIndex, fullContent);
            }
          } catch (e) {
            console.debug("Failed to parse SSE data:", line);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
</script>

<style scoped></style>
