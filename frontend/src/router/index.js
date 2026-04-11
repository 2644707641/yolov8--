import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

export const routes = [
  {
    path: "/",
    component: () => import("../layouts/AppShell.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/overview",
      },
      {
        path: "overview",
        name: "Overview",
        component: () => import("../views/Overview.vue"),
        meta: { title: "系统概览" },
      },
      {
        path: "workspace",
        name: "Workspace",
        component: () => import("../views/Dashboard.vue"),
        meta: { title: "识别工作台" },
      },
      {
        path: "history",
        name: "History",
        component: () => import("../views/History.vue"),
        meta: { title: "历史记录中心" },
      },
      {
        path: "model-weights",
        name: "ModelWeights",
        component: () => import("../views/ModelWeights.vue"),
        meta: { title: "模型与权重" },
      },
      {
        path: "realtime",
        name: "Realtime",
        component: () => import("../views/Realtime.vue"),
        meta: { title: "实时监控" },
      },
      {
        path: "settings",
        name: "Settings",
        component: () => import("../views/Settings.vue"),
        meta: { title: "系统设置" },
      },
    ],
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
    meta: { requiresGuest: true },
  },
  {
    path: "/dashboard",
    redirect: "/workspace",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (!authStore.ready) {
    try {
      await authStore.initAuth();
    } catch (error) {
      console.error("路由导航前初始化认证失败:", error);
    }
  }

  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const requiresGuest = to.matched.some((record) => record.meta.requiresGuest);

  if (requiresAuth && !authStore.user) {
    next("/login");
    return;
  }

  if (requiresGuest && authStore.user) {
    next("/overview");
    return;
  }

  next();
});

export default router;
