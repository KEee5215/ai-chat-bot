<template>
  <div v-if="props.role === 'user'" :class="chatClass">
    <div class="chat-image avatar">
      <div class="w-10 rounded-full">
        <img
          src="https://img.daisyui.com/images/profile/demo/yellingcat@192.webp"
        />
      </div>
    </div>
    <div :class="chatBubbleClass">
      {{ props.content }}
    </div>
  </div>
  <div v-else class="m-6 px-4 py-6">
    <div class="max-w-4xl mx-auto">
      <AIMarkdown :content="content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import AIMarkdown from "../chat/AIMarkdown.vue";

const props = defineProps(["role", "content"]);

// 如果props.role为"user"，计算成chat-end
const chatClass = computed(() => {
  return props.role === "user" ? "chat chat-end " : "chat chat-start";
});

const chatBubbleClass = computed(() => {
  return props.role === "user"
    ? "chat-bubble-success chat-bubble"
    : "chat-bubble";
});
</script>

<style scoped></style>
