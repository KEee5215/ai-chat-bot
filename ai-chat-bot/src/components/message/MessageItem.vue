<template>
  <div :class="chatClass">
    <div :class="chatBubbleClass">{{ content }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps(["role", "content"]);

// 如果props.role为"user"，计算成chat-end
const chatClass = computed(() => {
  return props.role === "user" ? "chat chat-end " : "chat chat-start";
});

const chatBubbleClass = computed(() => {
  return props.role === "user" ? "chat-bubble-info chat-bubble" : "chat-bubble";
});
</script>

<style scoped></style>
