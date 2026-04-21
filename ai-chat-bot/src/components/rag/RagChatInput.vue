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
// import { useSendMessageStream } from "@/hooks/useSendMessageStream";
import uploadFile from "@/hooks/useFileUpload";
import { ragChat } from "@/api/rag/rag";
import { useMessageStore } from "@/stores/message";

const messageStore = useMessageStore();

const newMessage = ref<string>("");
const isLoading = ref(false);
let isNull = true;

// const { sendMessage: sendMsg } = useSendMessageStream();

watch(newMessage, (newValue) => {
  isNull = !newValue.trim();
});

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (files && files.length > 0) {
    try {
      await uploadFile(files[0] as File);
      console.log("文件上传完成");
    } catch (error) {
      console.error("文件上传失败:", error);
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
    // 1. 添加用户消息到 store
    messageStore.addUserMessage(userInput);

    // 2. 调用 RAG API
    const session_id = messageStore.sessionId;
    const document_ids = messageStore.documentIds;
    const res: any = await ragChat(session_id, document_ids, userInput);
    
    console.log("RAG 响应:", res);

    // 3. 添加 AI 回复到 store
    // 根据后端返回格式调整，假设返回 { answer: "..." } 或直接返回字符串
    const aiContent = res.answer || res.data?.answer || res.content || res;
    messageStore.addAIMessage(aiContent);
    
    // 4. 标记消息完成
    const lastIndex = messageStore.message.length - 1;
    messageStore.markMessageComplete(lastIndex);
  } catch (error) {
    console.error("RAG 问答失败:", error);
    // 可选：添加错误提示消息
    messageStore.addAIMessage("抱歉，回答失败，请稍后重试。");
    const lastIndex = messageStore.message.length - 1;
    messageStore.markMessageComplete(lastIndex);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped></style>
