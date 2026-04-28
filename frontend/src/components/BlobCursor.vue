<script setup>
import gsap from 'gsap'
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  color: { type: String, default: '#06b6d4' },
  zIndex: { type: Number, default: 9998 }
})

const dotRef = ref(null)
const canvasRef = ref(null)

const TRAIL_LEN = 28
const TRAIL_HEAD_R = 8
const TRAIL_LIFETIME_MS = 500

let trail = []
let animFrameId = null
let ctx = null

const hexToRgb = (hex) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `${r},${g},${b}`
}

const resizeCanvas = () => {
  if (!canvasRef.value) return
  canvasRef.value.width = window.innerWidth
  canvasRef.value.height = window.innerHeight
}

const drawTrail = () => {
  if (!ctx) return
  const now = performance.now()
  trail = trail.filter(p => now - p.t < TRAIL_LIFETIME_MS)
  if (ctx) {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight)
    const rgb = hexToRgb(props.color)
    trail.forEach((pos, i) => {
      const ageRatio = 1 - (now - pos.t) / TRAIL_LIFETIME_MS
      const idxRatio = 1 - i / TRAIL_LEN
      const ratio = Math.min(ageRatio, idxRatio)
      if (ratio <= 0) return
      const r = TRAIL_HEAD_R * ratio
      const alpha = ratio * 0.55
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(${rgb},${alpha.toFixed(3)})`
      ctx.fill()
    })
  }
  animFrameId = requestAnimationFrame(drawTrail)
}

const handleMove = (e) => {
  const x = 'clientX' in e ? e.clientX : e.touches[0].clientX
  const y = 'clientY' in e ? e.clientY : e.touches[0].clientY
  trail.unshift({ x, y, t: performance.now() })
  if (trail.length > TRAIL_LEN) trail.length = TRAIL_LEN
  gsap.to(dotRef.value, { x, y, duration: 0.06, ease: 'power3.out', overwrite: true })
}


onMounted(() => {
  trail = []
  gsap.set(dotRef.value, { xPercent: -50, yPercent: -50 })
  ctx = canvasRef.value?.getContext('2d')
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  window.addEventListener('mousemove', handleMove)
  window.addEventListener('touchmove', handleMove)
  animFrameId = requestAnimationFrame(drawTrail)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMove)
  window.removeEventListener('touchmove', handleMove)
  window.removeEventListener('resize', resizeCanvas)
  if (animFrameId) cancelAnimationFrame(animFrameId)
  gsap.killTweensOf(dotRef.value)
  ctx = null
  trail = []
})
</script>

<template>
  <div
    class="fixed inset-0 w-full h-full"
    :style="{ zIndex: props.zIndex, pointerEvents: 'none' }"
  >
    <!-- 彗星尾托画布 -->
    <canvas ref="canvasRef" class="absolute inset-0" />
    <!-- 精准小圆点 -->
    <div
      ref="dotRef"
      class="absolute will-change-transform"
      :style="{
        left: 0,
        top: 0,
        width: '16px',
        height: '16px',
        borderRadius: '50%',
        backgroundColor: props.color,
        boxShadow: `0 0 10px 4px ${props.color}80`
      }"
    />
  </div>
</template>
