<template>
  <div class="auth-page bg-black text-white selection:bg-blue-500/30">

    <!-- WebGL 3D 渲染容器 (底层) -->
    <div ref="canvasContainer" class="fixed inset-0 z-0 opacity-80 mix-blend-screen pointer-events-none"></div>

    <!-- 登录成功顶部横幅 -->
    <Transition name="banner">
      <div v-if="loginSuccess" class="fixed top-0 left-0 right-0 z-[100] flex items-center justify-center py-3 bg-emerald-500/90 backdrop-blur-md shadow-[0_4px_30px_rgba(16,185,129,0.4)]">
        <span class="font-mono text-xs tracking-[0.3em] text-white uppercase">✓ 识别通过 · 正在进入停车监控台...</span>
      </div>
    </Transition>

    <!-- 转场遮罩 -->
    <div ref="portalOverlay" class="fixed inset-0 z-[90] bg-cyan-600 pointer-events-none" style="opacity: 0;"></div>

    <!-- 认证表单层 -->
    <div class="auth-container min-h-screen flex items-center justify-end pr-12 md:pr-32 overflow-hidden relative font-sans">

      <!-- 左侧装饰：大型动态文字背景 -->
      <div class="absolute left-12 top-1/2 -translate-y-1/2 select-none pointer-events-none opacity-5 hidden lg:block">
        <h2 class="text-[15rem] font-black leading-none uppercase tracking-tighter">
          泊位<br/>智识
        </h2>
      </div>

      <!-- 悬浮登录终端 -->
      <div ref="authTerminal" class="relative z-20 w-full max-w-lg">

        <!-- 动态扫描线 -->
        <div class="absolute -left-8 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-cyan-500 to-transparent animate-scan shadow-[0_0_15px_#06b6d4]"></div>

        <div class="space-y-12">
          <!-- 头部：全息投影感标题 -->
          <header class="relative animate-terminal">
            <div class="flex items-center gap-4 mb-4">
              <span class="w-12 h-px bg-cyan-500"></span>
              <span class="text-xs font-mono tracking-[0.4em] text-cyan-400 uppercase tracking-widest">YOLOv8 视觉识别系统: 待授权</span>
            </div>
            <h1 class="text-6xl font-black tracking-tighter leading-none italic">
              {{ isLogin ? '智停' : '注册' }}<br/>
              <span class="text-outline text-7xl">{{ isLogin ? '驭眼' : '入网' }}</span>
            </h1>
            <div class="mt-4 flex gap-2">
               <div v-for="i in 3" :key="i" class="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-ping" :style="{ animationDelay: `${i * 0.2}s` }"></div>
            </div>
          </header>

          <!-- 错误信息 -->
          <div v-if="authStore.error" class="animate-terminal text-[10px] text-red-500 font-mono tracking-widest animate-pulse">
            [ 警告 ] : {{ authStore.error }}
          </div>

          <!-- 注册成功提示 -->
          <div v-if="registerSuccess" class="animate-terminal text-[10px] text-emerald-400 font-mono tracking-widest">
            [ 成功 ] : 注册成功！请查收邮箱完成验证后登录。
          </div>

          <!-- 表单：无边框悬浮设计 -->
          <form @submit.prevent="handleSubmit" class="space-y-10 overflow-hidden py-2">
            <div v-for="field in currentFields" :key="field.id" class="animate-terminal group relative space-y-2">
              <label class="block text-xs font-bold tracking-[0.2em] text-slate-200 uppercase transition-colors group-focus-within:text-blue-400">
                {{ field.label }}
              </label>
              <div class="relative">
                <input
                  v-model="formData[field.id]"
                  :type="field.id === 'uid' ? 'text' : (fieldVisible[field.id] ? 'text' : 'password')"
                  class="w-full bg-transparent border-b border-white/30 py-6 text-2xl font-medium tracking-widest outline-none transition-all duration-500 text-white focus:border-cyan-500 placeholder:text-slate-600"
                  :class="{ 'pr-10': isLogin && (field.id === 'key' || field.id === 'confirm_key') }"
                  :placeholder="field.placeholder"
                  required
                />
                <button
                  v-if="isLogin && (field.id === 'key' || field.id === 'confirm_key')"
                  type="button"
                  @click="fieldVisible[field.id] = !fieldVisible[field.id]"
                  class="absolute right-0 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyan-400 transition-colors duration-300 p-2"
                  :aria-label="fieldVisible[field.id] ? '隐藏密码' : '显示密码'"
                >
                  <svg v-if="!fieldVisible[field.id]" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12c1.292 4.338 5.31 7.5 10.066 7.5.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                  </svg>
                </button>
              </div>
              <!-- 聚焦时的底部进度条 -->
              <div class="absolute bottom-0 left-0 w-0 h-px bg-cyan-500 transition-all duration-700 group-focus-within:w-full"></div>
            </div>

            <!-- 提示信息 (当密码不一致时) -->
            <div v-if="!isLogin && !passwordsMatch && formData.confirm_key" class="text-[10px] text-red-500 font-mono tracking-widest animate-pulse">
              [ 警告 ] : 两次输入的密码不一致
            </div>

            <!-- 提交动作 -->
            <div class="flex items-center gap-12 animate-terminal mt-4">
              <button
                type="submit"
                :disabled="(!isLogin && !passwordsMatch) || authStore.loading"
                class="magnetic-btn relative px-12 py-6 bg-cyan-600 disabled:bg-slate-800 disabled:text-slate-500 hover:bg-white hover:text-black transition-all duration-500 group overflow-hidden"
              >
                <span class="relative z-10 text-xs font-black uppercase tracking-[0.3em]">
                  {{ authStore.loading ? (isLogin ? '验证中...' : '注册中...') : (isLogin ? '登录智能停车平台' : '注册新账户') }}
                </span>
                <div class="absolute top-0 right-0 w-2 h-2 border-t border-r border-white group-hover:border-black"></div>
                <div class="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white group-hover:border-black"></div>
              </button>

              <div class="cursor-pointer group" @click="toggleMode">
                 <span class="text-[10px] font-mono text-slate-500 uppercase tracking-widest group-hover:text-white transition-colors">
                    {{ isLogin ? '注册新账户' : '返回登录' }}
                 </span>
                 <div class="w-full h-px bg-slate-800 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
              </div>
            </div>
          </form>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import * as THREE from 'three'
import gsap from 'gsap'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLogin = ref(true)
const authTerminal = ref(null)
const canvasContainer = ref(null)
const portalOverlay = ref(null)
const registerSuccess = ref(false)
const loginSuccess = ref(false)

let scene, camera, renderer, blob, animationId, geometry

// 密码字段可见性控制
const fieldVisible = reactive({
  key: false,
  confirm_key: false
})

// 表单数据绑定
const formData = reactive({
  uid: '',
  key: '',
  confirm_key: ''
})

// 动态字段计算
const currentFields = computed(() => {
  const baseFields = [
    { id: 'uid', label: '登录邮箱', type: 'email', placeholder: 'your@email.com' },
    { id: 'key', label: '访问密码', type: 'password', placeholder: '••••••••' }
  ]

  if (!isLogin.value) {
    baseFields.push({ id: 'confirm_key', label: '确认密码', type: 'password', placeholder: '••••••••' })
  }

  return baseFields
})

// 验证两次密码是否一致
const passwordsMatch = computed(() => {
  return formData.key === formData.confirm_key
})

// --- WebGL 核心逻辑 ---
const initThree = () => {
  if (!canvasContainer.value) return

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  camera.position.z = 5

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  canvasContainer.value.appendChild(renderer.domElement)

  geometry = new THREE.IcosahedronGeometry(2, 16)
  const material = new THREE.MeshPhysicalMaterial({
    color: 0x06b6d4,
    metalness: 0.1,
    roughness: 0.05,
    emissive: 0x0891b2,
    emissiveIntensity: 0.2,
    transmission: 0.9,
    thickness: 1,
  })

  blob = new THREE.Mesh(geometry, material)
  blob.material.side = THREE.DoubleSide
  scene.add(blob)

  const pointLight1 = new THREE.PointLight(0x06b6d4, 50, 20)
  pointLight1.position.set(5, 5, 5)
  scene.add(pointLight1)

  const pointLight2 = new THREE.PointLight(0x3b82f6, 30, 20)
  pointLight2.position.set(-5, -5, 5)
  scene.add(pointLight2)

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)

  const clock = new THREE.Clock()
  const positionAttribute = geometry.getAttribute('position')
  const vertexCount = positionAttribute.count
  const vertex = new THREE.Vector3()
  const animate = () => {
    const elapsedTime = clock.getElapsedTime()

    for (let i = 0; i < vertexCount; i++) {
      vertex.fromBufferAttribute(positionAttribute, i)
      const offset = 0.15 * Math.sin(vertex.x * 2 + elapsedTime * 1.5) +
                     0.15 * Math.sin(vertex.y * 1.5 + elapsedTime * 2)
      vertex.normalize().multiplyScalar(2 + offset)
      positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z)
    }
    positionAttribute.needsUpdate = true
    blob.rotation.y += 0.005
    renderer.render(scene, camera)
    animationId = requestAnimationFrame(animate)
  }
  animationId = requestAnimationFrame(animate)

  // 初始位置：偏左显示，不遮挡表单
  blob.position.x = -3
  blob.position.y = 0
  blob.position.z = -2
}

const handleResize = () => {
  if (!camera || !renderer) return
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
}

const toggleMode = () => {
  registerSuccess.value = false

  gsap.to('.animate-terminal', {
    x: -20,
    opacity: 0,
    stagger: 0.05,
    duration: 0.4,
    ease: "power2.in",
    onComplete: () => {
      isLogin.value = !isLogin.value
      formData.confirm_key = ''

      gsap.fromTo('.animate-terminal',
        { x: 20, opacity: 0 },
        { x: 0, opacity: 1, stagger: 0.08, duration: 0.8, ease: "expo.out" }
      )
    }
  })
}

const handleSubmit = async () => {
  if (!isLogin.value && !passwordsMatch.value) return

  if (isLogin.value) {
    const result = await authStore.login(formData.uid, formData.key)
    if (result.success) {
      // 显示成功横幅
      loginSuccess.value = true
      // 登录成功的动效：圆球扩大 → 停顿 → 蓝色出现 → 跳转
      gsap.to(authTerminal.value, { x: 50, opacity: 0, duration: 0.8, ease: "expo.in" })
      // 提升canvas层级到最顶层，移除混合模式干扰，让球体可见
      canvasContainer.value.style.zIndex = '100'
      canvasContainer.value.style.mixBlendMode = 'normal'
      canvasContainer.value.style.opacity = '1'
      canvasContainer.value.style.backgroundColor = '#020d10'

      const tl = gsap.timeline({ delay: 0.3 })
      // 第一阶段：圆球扩大、移到屏幕中心、从透光变实心
      tl.to(blob.position, { x: 0, y: 0, z: 3.5, duration: 1.2, ease: "power3.inOut" }, 0)
      tl.to(blob.scale, { x: 4, y: 4, z: 4, duration: 1.2, ease: "power3.inOut" }, 0)
      tl.to(blob.material, { transmission: 0, emissiveIntensity: 2, opacity: 1, duration: 1.0, ease: "power2.inOut" }, 0)
      // 第二阶段：停顿0.3s后，蓝色遮罩淡入覆盖
      tl.to(portalOverlay.value, { opacity: 1, duration: 0.5, ease: "power2.inOut" }, "+=0.3")
      // 第三阶段：跳转
      tl.call(() => { router.push('/overview') })
    }
  } else {
    const result = await authStore.register(formData.uid, formData.key)
    if (result.success) {
      registerSuccess.value = true
      formData.uid = ''
      formData.key = ''
      formData.confirm_key = ''
    }
  }
}

onMounted(() => {
  initThree()
  window.addEventListener('resize', handleResize)

  gsap.from('.animate-terminal', {
    duration: 1.5,
    x: 100,
    opacity: 0,
    stagger: 0.15,
    ease: "expo.out",
    delay: 0.3
  })

  const btn = document.querySelector('.magnetic-btn')
  if (btn) {
    btn.addEventListener('mousemove', (e) => {
      const { left, top, width, height } = btn.getBoundingClientRect()
      const x = (e.clientX - (left + width / 2)) * 0.3
      const y = (e.clientY - (top + height / 2)) * 0.3
      gsap.to(btn, { x, y, duration: 0.3 })
    })
    btn.addEventListener('mouseleave', () => {
      gsap.to(btn, { x: 0, y: 0, duration: 0.5, ease: "elastic.out(1, 0.3)" })
    })
  }
})

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
  renderer?.dispose()
  geometry?.dispose()
  blob?.material?.dispose()
  scene?.clear()
})
</script>

<style scoped>
.auth-page {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  overflow-x: hidden;
  background-color: #020d10;
}

.auth-container {
  background: transparent;
}

.text-outline {
  -webkit-text-stroke: 1px rgba(255, 255, 255, 0.15);
  color: transparent;
}

@keyframes scan {
  0% { transform: translateY(-10%); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: translateY(110%); opacity: 0; }
}
.animate-scan {
  animation: scan 4s infinite linear;
}

input::placeholder {
  opacity: 0.2;
}

.magnetic-btn::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transition: 0.5s;
}
.magnetic-btn:hover::after {
  left: 150%;
}

button:disabled {
  cursor: not-allowed;
  filter: grayscale(1);
  opacity: 0.5;
}

.banner-enter-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.banner-leave-active {
  transition: all 0.4s ease-in;
}
.banner-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}
.banner-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
