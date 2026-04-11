<script setup>
import gsap from 'gsap'
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  blobType: { type: String, default: 'circle' },
  fillColor: { type: String, default: '#06b6d4' },
  trailCount: { type: Number, default: 3 },
  sizes: { type: Array, default: () => [60, 125, 75] },
  innerSizes: { type: Array, default: () => [20, 35, 25] },
  innerColor: { type: String, default: 'rgba(255,255,255,0.8)' },
  opacities: { type: Array, default: () => [0.6, 0.6, 0.6] },
  shadowColor: { type: String, default: 'rgba(0,0,0,0.75)' },
  shadowBlur: { type: Number, default: 5 },
  shadowOffsetX: { type: Number, default: 10 },
  shadowOffsetY: { type: Number, default: 10 },
  filterId: { type: String, default: 'blob' },
  filterStdDeviation: { type: Number, default: 30 },
  filterColorMatrixValues: { type: String, default: '1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 35 -10' },
  useFilter: { type: Boolean, default: true },
  fastDuration: { type: Number, default: 0.1 },
  slowDuration: { type: Number, default: 0.5 },
  fastEase: { type: String, default: 'power3.out' },
  slowEase: { type: String, default: 'power1.out' },
  zIndex: { type: Number, default: 100 }
})

const blobsRef = ref([])

const handleMove = (e) => {
  const x = 'clientX' in e ? e.clientX : e.touches[0].clientX
  const y = 'clientY' in e ? e.clientY : e.touches[0].clientY

  blobsRef.value.forEach((el, i) => {
    if (!el) return
    const isLead = i === 0
    const halfW = props.sizes[i] / 2
    const halfH = props.sizes[i] / 2
    gsap.to(el, {
      x: x - halfW,
      y: y - halfH,
      duration: isLead ? props.fastDuration : props.slowDuration,
      ease: isLead ? props.fastEase : props.slowEase
    })
  })
}

onMounted(() => {
  window.addEventListener('mousemove', handleMove)
  window.addEventListener('touchmove', handleMove)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMove)
  window.removeEventListener('touchmove', handleMove)
})
</script>

<template>
  <div
    class="fixed inset-0 w-full h-full"
    :style="{ zIndex: props.zIndex, pointerEvents: 'none' }"
  >
    <svg v-if="props.useFilter" class="absolute w-0 h-0">
      <filter :id="props.filterId">
        <feGaussianBlur in="SourceGraphic" result="blur" :stdDeviation="props.filterStdDeviation" />
        <feColorMatrix in="blur" :values="props.filterColorMatrixValues" />
      </filter>
    </svg>

    <div
      class="absolute inset-0 overflow-hidden cursor-default select-none"
      :style="{
        filter: props.useFilter ? `url(#${props.filterId})` : undefined
      }"
    >
      <div
        v-for="(_, i) in props.trailCount"
        :key="i"
        :ref="el => { blobsRef[i] = el }"
        class="absolute will-change-transform"
        :style="{
          left: 0,
          top: 0,
          width: `${props.sizes[i]}px`,
          height: `${props.sizes[i]}px`,
          borderRadius: props.blobType === 'circle' ? '50%' : '0',
          backgroundColor: props.fillColor,
          opacity: props.opacities[i],
          boxShadow: `${props.shadowOffsetX}px ${props.shadowOffsetY}px ${props.shadowBlur}px 0 ${props.shadowColor}`
        }"
      >
        <div
          class="absolute"
          :style="{
            width: `${props.innerSizes[i]}px`,
            height: `${props.innerSizes[i]}px`,
            top: `${(props.sizes[i] - props.innerSizes[i]) / 2}px`,
            left: `${(props.sizes[i] - props.innerSizes[i]) / 2}px`,
            backgroundColor: props.innerColor,
            borderRadius: props.blobType === 'circle' ? '50%' : '0'
          }"
        />
      </div>
    </div>
  </div>
</template>
