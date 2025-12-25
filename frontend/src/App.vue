<template>
  <div id="app" class="min-h-screen">
    <router-view v-slot="{ Component, route }">
      <keep-alive :include="['Dashboard', 'History']">
        <component :is="Component" :key="route.path" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  await authStore.initAuth()
})
</script>
