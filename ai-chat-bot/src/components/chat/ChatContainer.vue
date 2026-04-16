<template>
  <div class="flex flex-col h-full w-full">
    <div class="flex-1 overflow-y-auto pb-32">
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
import { ref } from "vue";
import MessageItem from "../message/MessageItem.vue";

import { useMessageStore } from "@/stores/message";
import ChatInput from "./ChatInput.vue";

const messageStore = useMessageStore();

const message = ref(messageStore.message);

const route = useRoute();
//通过这个id来查询对话历史
const id = ref(route.params.id);

//把id存入pinia
console.log(route.params.id);
</script>
