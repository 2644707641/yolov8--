<template>
  <div
    data-testid="app-shell-root"
    class="relative h-screen overflow-hidden"
    style="background-color: #020d10;"
  >
    <div class="absolute inset-0">
      <div
        class="absolute inset-0"
        style="background: linear-gradient(to bottom right, #020d10, #041520, #010a0d);"
      ></div>
      <div class="absolute inset-0 bg-grid opacity-10"></div>
      <div
        class="absolute -top-24 left-1/4 h-80 w-80 rounded-full bg-cyan-500/20 blur-3xl"
      ></div>
      <div
        class="absolute top-1/2 -right-32 h-[420px] w-[420px] -translate-y-1/2 rounded-full bg-blue-500/15 blur-3xl"
      ></div>
      <div
        class="absolute bottom-0 left-0 h-[360px] w-[360px] rounded-full bg-cyan-900/20 blur-3xl"
      ></div>
    </div>

    <div class="pointer-events-none absolute inset-0 z-40">
      <StaggeredMenu
        data-testid="system-nav"
        class-name="app-shell-staggered-menu h-full"
        position="left"
        :items="navItems"
        :social-items="[]"
        :display-socials="false"
        :display-item-numbering="true"
        menu-button-color="#e2e8f0"
        open-menu-button-color="#ffffff"
        :change-menu-color-on-open="true"
        :colors="['#67e8f9', '#22d3ee', '#0891b2']"
        logo-url=""
        accent-color="#0891b2"
      />
    </div>

    <div
      data-testid="app-shell-main-column"
      class="relative z-10 flex h-full min-h-0 flex-col overflow-hidden"
    >
      <header
        data-testid="app-shell-header"
        class="sticky top-0 z-30 shrink-0 border-b border-white/10 bg-white/5 backdrop-blur-xl"
      >
        <div class="flex items-center justify-between px-6 py-3 lg:px-10">
          <div class="flex items-center gap-4 pl-16 md:pl-24">
            <div>
              <p class="text-xs uppercase tracking-[0.35em] text-slate-400/80">
                系统控制台
              </p>
              <h1 class="text-xl font-semibold text-white">
                {{ pageTitle }}
              </h1>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="hidden text-right text-xs text-slate-400/80 md:block">
              <div class="uppercase tracking-[0.3em]">当前账户</div>
              <div class="text-sm font-medium text-white">
                {{ authStore.user?.email || "未登录" }}
              </div>
            </div>
            <router-link to="/settings" class="btn-secondary text-sm">
              系统设置
            </router-link>
            <button
              class="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300 transition hover:border-red-500/50 hover:bg-red-500/20 hover:text-red-200"
              @click="authStore.logout"
            >
              退出登录
            </button>
          </div>
        </div>
      </header>

      <main
        data-testid="app-shell-content"
        class="min-h-0 flex-1 overflow-y-auto px-6 pt-6 lg:px-10"
      >
        <router-view v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import StaggeredMenu from "../components/StaggeredMenu.vue";
import { useAuthStore } from "../stores/auth";

const route = useRoute();
const authStore = useAuthStore();

const pageTitle = computed(() => route.meta?.title || "控制台");

const navItems = [
  { label: "系统概览", ariaLabel: "查看系统概览", link: "/overview" },
  { label: "识别工作台", ariaLabel: "进入识别工作台", link: "/workspace" },
  { label: "历史记录", ariaLabel: "查看历史记录", link: "/history" },
  { label: "模型管理", ariaLabel: "进入模型管理", link: "/model-weights" },
  { label: "实时监控", ariaLabel: "查看实时监控", link: "/realtime" },
  { label: "系统设置", ariaLabel: "进入系统设置", link: "/settings" },
];
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
