<template>
  <div
    class="glitch-text"
    :data-text="text"
    :class="{
      'glitch-text--hover': enableOnHover,
      'glitch-text--shadows': enableShadows
    }"
    :style="{ '--glitch-duration': animationDuration }"
  >
    {{ text }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  children: {
    type: String,
    required: true
  },
  speed: {
    type: Number,
    default: 1
  },
  enableShadows: {
    type: Boolean,
    default: false
  },
  enableOnHover: {
    type: Boolean,
    default: false
  }
})

const text = computed(() => props.children)

const animationDuration = computed(() => {
  const duration = props.speed > 0 ? props.speed : 1
  return `${duration}s`
})
</script>

<style scoped>
.glitch-text {
  position: relative;
  color: #ffffff;
  font-size: clamp(2.5rem, 6vw, 5rem);
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  animation: glitch var(--glitch-duration, 1s) infinite;
}

.glitch-text::before,
.glitch-text::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  animation: glitch var(--glitch-duration, 1s) infinite;
}

.glitch-text::before {
  left: 2px;
  text-shadow: -2px 0 #ff00c1;
  clip-path: inset(0 0 45% 0);
}

.glitch-text::after {
  left: -2px;
  text-shadow: -2px 0 #00e7ff;
  clip-path: inset(55% 0 0 0);
}

.glitch-text--shadows {
  text-shadow:
    0 0 12px rgba(255, 255, 255, 0.65),
    0 0 32px rgba(255, 255, 255, 0.45);
}

.glitch-text--hover {
  animation-play-state: paused;
}

.glitch-text--hover::before,
.glitch-text--hover::after {
  animation-play-state: paused;
}

.glitch-text--hover:hover,
.glitch-text--hover:hover::before,
.glitch-text--hover:hover::after {
  animation-play-state: running;
}

@keyframes glitch {
  0% {
    transform: translate3d(0, 0, 0);
  }
  20% {
    transform: translate3d(-3px, 2px, 0);
  }
  40% {
    transform: translate3d(3px, -2px, 0);
  }
  60% {
    transform: translate3d(-2px, 3px, 0);
  }
  80% {
    transform: translate3d(2px, -3px, 0);
  }
  100% {
    transform: translate3d(0, 0, 0);
  }
}
</style>
