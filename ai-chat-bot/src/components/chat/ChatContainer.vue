<template>
  <div class="flex flex-col h-full w-full">
    <div class="flex-1 overflow-y-auto py-32">
      <MessageItem
        v-for="item in message"
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
import { computed, onMounted, ref } from "vue";
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

const message = ref<Message[]>();

onMounted(async () => {
  const sessionId = route.params.id as string;
  messageStore.setSessionId(sessionId);
  console.log(sessionId);
  let res: any = await getMessage(sessionId, 10);
  console.log(res);
  message.value = res;
});
</script>
