import { createRouter, createWebHistory } from "vue-router";
import ChatView from "../views/ChatView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: ChatView,
      redirect: "/chat",
      children: [
        {
          // 当 /user/:id/profile 匹配成功
          // UserProfile 将被渲染到 User 的 <router-view> 内部
          path: "/chat/:id",
          name: "chat",
          component: () => import("@/components/chat/ChatContainer.vue"),
        },
        {
          path: "/rag/:id",
          name: "rag",
          component: () => import("@/components/rag/RagChat.vue"),
        },
      ],
    },
    {
      path: "/login",
      name: "login",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/chat",
      name: "chatWelcome",
      component: () => import("@/components/chat/ChatWelcome.vue"),
    },
    {
      path: "/test",
      name: "test",
      component: () => import("../views/TestView.vue"),
    },
  ],
});

export default router;
