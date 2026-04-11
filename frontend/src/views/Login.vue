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
    <div ref="portalOverlay" class="fixed inset-0 z-[90] bg-cyan-600 scale-y-0 origin-bottom pointer-events-none opacity-0"></div>

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
              <input
                v-model="formData[field.id]"
                :type="field.type"
                class="w-full bg-transparent border-b border-white/30 py-6 text-2xl font-medium tracking-widest outline-none transition-all duration-500 text-white focus:border-cyan-500 placeholder:text-slate-600"
                :placeholder="field.placeholder"
                required
              />
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

let scene, camera, renderer, blob

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

  const geometry = new THREE.IcosahedronGeometry(2, 64)
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
  const animate = () => {
    const elapsedTime = clock.getElapsedTime()
    const positionAttribute = geometry.getAttribute('position')
    const vertex = new THREE.Vector3()

    for (let i = 0; i < positionAttribute.count; i++) {
      vertex.fromBufferAttribute(positionAttribute, i)
      const offset = 0.15 * Math.sin(vertex.x * 2 + elapsedTime * 1.5) +
                     0.15 * Math.sin(vertex.y * 1.5 + elapsedTime * 2)
      vertex.normalize().multiplyScalar(2 + offset)
      positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z)
    }
    positionAttribute.needsUpdate = true
    blob.rotation.y += 0.005
    renderer.render(scene, camera)
    requestAnimationFrame(animate)
  }
  animate()

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
      // 登录成功的动效
      gsap.to(authTerminal.value, { x: 50, opacity: 0, duration: 1, ease: "expo.in" })
      gsap.to(blob.scale, { x: 5, y: 5, z: 5, duration: 1.8, ease: "power4.inOut" })
      gsap.to(blob.position, { z: 2, duration: 1.8, ease: "power4.inOut" })
      // 蓝色遮罩展开
      gsap.to(portalOverlay.value, {
        opacity: 1,
        scaleY: 1,
        duration: 1.2,
        ease: "expo.inOut",
        delay: 1.5,
      })
      // 遮罩展开后保持片刻，再缓慢淡出进入控制台
      gsap.to(portalOverlay.value, {
        opacity: 0,
        duration: 1.5,
        ease: "power2.inOut",
        delay: 3.5,
        onComplete: () => {
          router.push('/overview')
        }
      })
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
  window.removeEventListener('resize', handleResize)
  renderer?.dispose()
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
