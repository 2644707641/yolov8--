<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-950">
    <GlitchText
      children="欢迎"
      :speed="0.5"
      :enable-shadows="true"
      :enable-on-hover="false"
    />
  </div>
</template>

<script setup lang="ts">
import GlitchText from './GlitchText.vue'
</script>
