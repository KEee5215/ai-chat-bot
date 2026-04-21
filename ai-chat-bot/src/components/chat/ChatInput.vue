<template>
  <div class="flex flex-col gap-2 w-full max-w-2xl mx-auto px-4 py-4">
    <input
      type="file"
      class="file-input file-input-ghost w-full"
      @click="handleFileSelect"
    />
    <div class="flex gap-2 items-end">
      <textarea
        placeholder="type something ..."
        class="textarea flex-1 resize-none min-h-12"
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
  </div>
</template>

<script setup lang="ts">
import SendIcon from "../icons/SendIcon.vue";
import { ref, watch } from "vue";
import { useSendMessageStream } from "@/hooks/useSendMessageStream";
import uploadFile from "@/hooks/useFileUpload";
import { useMessageStore } from "@/stores/message";

const messageStore = useMessageStore();

const newMessage = ref<string>("");
const isLoading = ref(false);
let isNull = true;

const { sendMessage: sendMsg } = useSendMessageStream();

watch(newMessage, (newValue) => {
  isNull = !newValue.trim();
});

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (files && files.length > 0) {
    try {
      const sessionId = messageStore.sessionId;
      if (!sessionId) {
        console.error("未找到会话ID");
        return;
      }
      await uploadFile(files[0] as File, sessionId);
      console.log("文件上传完成");
    } catch (error) {
      console.error("文件上传失败:", error);
      // 可选：显示错误提示
      alert(error instanceof Error ? error.message : "文件上传失败");
    }
    // 重置 input
    target.value = "";
  }
}

async function sendMessage() {
  if (!newMessage.value.trim()) return;

  const userInput = newMessage.value;
  newMessage.value = "";
  isLoading.value = true;

  try {
    await sendMsg(userInput);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped></style>
