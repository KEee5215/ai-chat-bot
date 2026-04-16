<template>
  <div class="flex flex-col h-full w-full">
    <div class="flex-1 overflow-y-auto pb-24">
      <MessageItem
        v-for="item in message"
        :content="item.content"
        :role="item.role"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { ref } from "vue";
import MessageItem from "../message/MessageItem.vue";
import ChatInput from "./ChatInput.vue";
import SendIcon from "../icons/SendIcon.vue";

const message = ref([
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  {
    role: "assistant",
    content: "hello,aisdiohasdoaisdhasidh<br>nsdnaiosdioasdadaiosdn",
  },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
  { role: "user", content: "hello" },
  { role: "assistant", content: "hello" },
]);

const route = useRoute();
//通过这个id来查询对话历史
const id = ref(route.params.id);

//把id存入pinia
console.log(route.params.id);
</script>
