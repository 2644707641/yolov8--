<template>
  <router-view />
  <!-- 全局转场遮罩：登录→控制台时，蓝色铺满后缓慢淡出 -->
  <div
    v-if="transitionOverlay"
    class="fixed inset-0 z-[9999] pointer-events-none"
    :style="{ backgroundColor: '#0891b2', opacity: transitionOpacity }"
  ></div>
  <!-- 斑点光标：仅认证后页面显示 -->
  <BlobCursor
    v-if="showCursor"
    color="#06b6d4"
    :zIndex="9998"
  />
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import BlobCursor from './components/BlobCursor.vue'

const authStore = useAuthStore()
const router = useRouter()

const transitionOverlay = ref(false)
const transitionOpacity = ref(1)

const showCursor = ref(true)

// 监听路由变化：从登录页进入时，显示蓝色遮罩并淡出
const unregisterAfterEach = router.afterEach((to, from) => {
  if (from.path === '/login' && to.path !== '/login') {
    transitionOverlay.value = true
    transitionOpacity.value = 1
    gsap.to({ val: 1 }, {
      val: 0,
      duration: 1.2,
      ease: "power2.inOut",
      delay: 0.1,
      onUpdate: function() {
        transitionOpacity.value = this.targets()[0].val
      },
      onComplete: () => {
        transitionOverlay.value = false
      }
    })
  }
})

onUnmounted(() => unregisterAfterEach())

authStore.initAuth()
</script>
