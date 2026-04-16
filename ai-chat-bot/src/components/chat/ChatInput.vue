<template>
  <div
    class="flex gap-2 w-600 max-w-full px-4 py-4 items-center justify-center"
  >
    <textarea
      placeholder="type something ..."
      class="textarea flex-1 resize-none min-h-12 max-w-120"
    >
    </textarea>
    <button class="btn btn-neutral flex-shrink-0 btn-circle">
      <SendIcon></SendIcon>
    </button>
  </div>
</template>

<script setup lang="ts">
import SendIcon from "../icons/SendIcon.vue";
</script>

<style scoped></style>
