<script setup lang="ts">
import { computed } from "vue";
import markdownit from "markdown-it";
import hljs from "highlight.js";
import "highlight.js/styles/atom-one-dark.css";
import DOMPurify from "dompurify";

// 自定义代码块渲染
const md = markdownit({
  highlight: (str: any, lang: any) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code class="language-${lang}">${
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
    ADD_TAGS: ["iframe", "span"],
    ADD_ATTR: ["src", "allow", "allowfullscreen", "class"],
    ALLOWED_ATTR: ["class", "src", "allow", "allowfullscreen"],
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
  background: #282c34 !important;
  padding: 16px !important;
  border-radius: 8px !important;
  overflow-x: auto !important;
  margin-bottom: 1rem !important;
  border: 1px solid #3e4451 !important;
}

.ai-markdown code {
  font-family: "JetBrains Mono", monospace !important;
  font-size: 14px !important;
  color: #abb2bf !important;
  line-height: 1.5 !important;
}

.ai-markdown pre code {
  background: transparent !important;
  color: inherit !important;
  padding: 0 !important;
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

/* 行内代码样式 */
.ai-markdown p code {
  background: #f5f5f5 !important;
  color: #d73a49 !important;
  padding: 2px 6px !important;
  border-radius: 3px !important;
  font-size: 0.9em !important;
}

/* 确保 highlight.js 的样式生效 */
.hljs {
  background-color: #282c34 !important;
  color: #abb2bf !important;
}

.hljs-string {
  color: #98c379 !important;
}

.hljs-number {
  color: #d19a66 !important;
}

.hljs-literal {
  color: #56b6c2 !important;
}

.hljs-attr {
  color: #e06c75 !important;
}

.hljs-title {
  color: #61afef !important;
}

.hljs-function {
  color: #61afef !important;
}

.hljs-keyword {
  color: #c678dd !important;
}
</style>
