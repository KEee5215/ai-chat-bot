<template>
  <div
    class="flex gap-2 w-600 max-w-full px-4 py-4 items-center justify-center"
  >
    <textarea
      placeholder="type something ..."
      class="textarea flex-1 resize-none min-h-12 max-w-120"
      v-model="newMessage"
    >
    </textarea>
    <button
      :disabled="isNull"
      class="btn btn-neutral btn-circle"
      @click="sendMessage"
    >
      <SendIcon></SendIcon>
    </button>
  </div>
</template>

<script setup lang="ts">
import SendIcon from "../icons/SendIcon.vue";
import { ref, watch } from "vue";
import { useMessageStore } from "@/stores/message";

const messageStore = useMessageStore();

const newMessage = ref<string>("");

let isNull = true;

watch(newMessage, (newValue) => {
  isNull = !newValue;
});

const sendMessage = () => {
  if (!newMessage.value) return;
  messageStore.addUserMessage(newMessage.value);
  newMessage.value = "";
};
</script>

<style scoped></style>
