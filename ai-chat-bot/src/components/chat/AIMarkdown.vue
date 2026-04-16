<script setup lang="ts">
import { computed } from "vue";
import markdownit from "markdown-it";
import hljs from "highlight.js";
import DOMPurify from "dompurify";

// 自定义代码块渲染
const md = markdownit({
  highlight: (str: any, lang: any) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${
          hljs.highlight(str, { language: lang }).value
        }</code></pre>`;
      } catch {}
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`;
  },
});

// 支持数学公式
// md.use(require("markdown-it-katex"));

const props = defineProps<{
  content: string;
}>();

const html = computed(() => {
  const rendered = md.render(props.content);
  return DOMPurify.sanitize(rendered, {
    ADD_TAGS: ["iframe"],
    ADD_ATTR: ["src", "allow", "allowfullscreen"],
  });
});
</script>

<template>
  <div class="ai-markdown" v-html="html" />
</template>

<style>
.ai-markdown h1 {
  font-size: 2.25rem !important;
  font-weight: bold !important;
  margin-bottom: 1rem !important;
  margin-top: 1.5rem !important;
  line-height: 2.5rem !important;
}

.ai-markdown h2 {
  font-size: 1.875rem !important;
  font-weight: bold !important;
  margin-bottom: 0.75rem !important;
  margin-top: 1.25rem !important;
  line-height: 2.25rem !important;
}

.ai-markdown h3 {
  font-size: 1.5rem !important;
  font-weight: bold !important;
  margin-bottom: 0.75rem !important;
  margin-top: 1rem !important;
  line-height: 2rem !important;
}

.ai-markdown h4 {
  font-size: 1.25rem !important;
  font-weight: bold !important;
  margin-bottom: 0.5rem !important;
  margin-top: 0.75rem !important;
  line-height: 1.75rem !important;
}

.ai-markdown h5 {
  font-size: 1.125rem !important;
  font-weight: bold !important;
  margin-bottom: 0.5rem !important;
  margin-top: 0.75rem !important;
  line-height: 1.5rem !important;
}

.ai-markdown h6 {
  font-size: 1rem !important;
  font-weight: bold !important;
  margin-bottom: 0.5rem !important;
  margin-top: 0.5rem !important;
  line-height: 1.5rem !important;
}

.ai-markdown p {
  margin-bottom: 0.75rem !important;
}

.ai-markdown ul,
.ai-markdown ol {
  margin-left: 1.5rem !important;
  margin-bottom: 0.75rem !important;
}

.ai-markdown li {
  margin-bottom: 0.25rem !important;
}

.ai-markdown pre {
  background: #1e1e1e !important;
  padding: 16px !important;
  border-radius: 8px !important;
  overflow-x: auto !important;
  margin-bottom: 1rem !important;
}

.ai-markdown code {
  font-family: "JetBrains Mono", monospace !important;
  font-size: 14px !important;
}

.ai-markdown table {
  border-collapse: collapse !important;
  width: 100% !important;
  margin-bottom: 0.75rem !important;
}

.ai-markdown th,
.ai-markdown td {
  border: 1px solid #ddd !important;
  padding: 8px !important;
}

.ai-markdown blockquote {
  border-left: 4px solid #d1d5db !important;
  padding-left: 1rem !important;
  font-style: italic !important;
  margin-bottom: 0.75rem !important;
}

.ai-markdown a {
  color: #2563eb !important;
  text-decoration: underline !important;
}

.ai-markdown a:hover {
  color: #1e40af !important;
}
</style>
