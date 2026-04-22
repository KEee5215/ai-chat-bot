<template>
  <div
    ref="scrollContainer"
    class="virtual-list-container"
    @scroll="handleScroll"
  >
    <!-- 幽灵元素，用于撑开滚动条总高度 -->
    <div class="phantom-element" :style="{ height: totalHeight + 'px' }"></div>

    <!-- 实际渲染的内容区域 -->
    <div
      class="rendered-content"
      :style="{ transform: `translateY(${offset}px)` }"
    >
      <div
        v-for="msg in visibleMessages"
        :key="msg.id"
        class="message-item"
        :style="{ height: itemHeight + 'px' }"
      >
        {{ msg.name || msg }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { getAllData } from "@/api/testDIR/test";
import { computed, onMounted, ref } from "vue";

const scrollContainer = ref<HTMLElement | null>(null);
const itemHeight = 80; // 预估的每条消息高度
const viewportHeight = 600; // 可视区域高度

const startIndex = ref(0);
const endIndex = ref(0);
const offset = ref(0);

// 计算总高度
const totalHeight = computed(() => messages.value.length * itemHeight);

// 计算可视区域内的消息
const visibleMessages = computed(() => {
  return messages.value.slice(startIndex.value, endIndex.value);
});

const messages = ref<any[]>([]);

const updateVisibleRange = () => {
  if (!scrollContainer.value) return;

  const scrollTop = scrollContainer.value.scrollTop;
  startIndex.value = Math.max(0, Math.floor(scrollTop / itemHeight));

  const visibleCount = Math.ceil(viewportHeight / itemHeight);
  endIndex.value = Math.min(
    startIndex.value + visibleCount + 5, // 多渲染几个作为缓冲
    messages.value.length,
  );

  offset.value = startIndex.value * itemHeight;
};

const handleScroll = () => {
  updateVisibleRange();
};

onMounted(async () => {
  try {
    const data = await getAllData();
    messages.value = Array.isArray(data) ? data : [];
    
    // 初始化可见范围
    updateVisibleRange();
  } catch (error) {
    console.error('获取数据失败:', error);
    // 如果API调用失败，使用模拟数据展示效果
    messages.value = Array.from({ length: 100 }, (_, i) => ({
      id: i + 1,
      name: `消息项 ${i + 1}`
    }));
    updateVisibleRange();
  }
});
</script>

<style scoped>
.virtual-list-container {
  height: 600px;
  overflow-y: auto;
  position: relative;
  border: 2px solid #409eff;
  background-color: #f5f7fa;
}

.phantom-element {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  visibility: hidden;
}

.rendered-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.message-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  margin: 4px 8px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-size: 16px;
  color: #333;
  border-left: 4px solid #409eff;
}
</style>
