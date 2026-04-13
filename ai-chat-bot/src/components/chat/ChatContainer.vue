<template>
  <div class="h1">对话容器{{ id }}</div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { ref } from "vue";

const route = useRoute();
//通过这个id来查询对话历史
const id = ref(route.params.id);

//把id存入pinia

console.log(route.params.id);
</script>

<style scoped></style>
