<template>
  <div class="login-container" :class="{ 'has-background': hasBackground }" :style="backgroundStyle">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-container" v-if="settings.system_logo">
          <img :src="settings.system_logo" alt="Logo" class="system-logo" />
        </div>
        <h1 class="system-name">{{ settings.system_name }}</h1>
        <p class="system-desc">{{ settings.system_intro }}</p>
      </div>

      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名 / Username"
            :prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码 / Password"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary"
            size="large"
            :loading="loading" 
            @click="handleLogin"
            class="login-btn"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-tips">
        <el-icon><InfoFilled /></el-icon>
        <span>默认账号：admin / admin123</span>
      </div>
      
      <div class="login-footer">
        {{ settings.copyright }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, InfoFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })
const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const settings = ref({
  system_name: 'DD-CLASS 班级管理系统',
  system_logo: '',
  system_intro: '一个现代化的班级管理系统',
  login_background: '',
  copyright: '© 2024 DD-CLASS',
  use_bing_background: true
})

const bingBackground = ref('')

const backgroundStyle = computed(() => {
  if (settings.value.use_bing_background && bingBackground.value) {
    return {
      backgroundImage: `url(${bingBackground.value})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  if (settings.value.login_background) {
    return {
      backgroundImage: `url(${settings.value.login_background})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {}
})

const hasBackground = computed(() => {
  return (settings.value.use_bing_background && bingBackground.value) || settings.value.login_background
})

const fetchBingBackground = async () => {
  try {
    const res = await api.get('/bing-background')
    if (res.data.url) {
      bingBackground.value = res.data.url
    }
  } catch (e) {
    console.error('获取Bing背景失败', e)
    bingBackground.value = 'https://www.bing.com/th?id=OHR.ZH-CN-8503073941_UHD.jpg'
  }
}

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const fetchSettings = async () => {
  try {
    const res = await api.get('/settings/public')
    settings.value = res.data
    document.title = res.data.system_name
  } catch (e) {
    console.error('获取系统设置失败', e)
  }
}

const handleLogin = async () => {
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(form.username, form.password)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        console.error(error)
        ElMessage.error('登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(async () => {
  await Promise.all([fetchSettings(), fetchBingBackground()])
})
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0c3483 0%, #0f5298 50%, #2cb5e8 100%);
  position: relative;
  overflow: hidden;
}

.login-container.has-background {
  background-size: cover !important;
  background-position: center !important;
}

.login-container.has-background::before,
.login-container.has-background::after {
  display: none;
}

.login-container:not(.has-background)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(44, 181, 232, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(44, 181, 232, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.login-container:not(.has-background)::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 40%,
    rgba(255, 255, 255, 0.05) 45%,
    rgba(255, 255, 255, 0.05) 55%,
    transparent 60%
  );
  animation: shine 15s infinite;
  pointer-events: none;
}

@keyframes shine {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 16px;
  width: 400px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.2),
    0 0 60px rgba(44, 181, 232, 0.2);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-container {
  margin-bottom: 15px;
}

.system-logo {
  max-width: 200px;
  max-height: 60px;
}

.system-name {
  margin: 10px 0;
  font-size: 24px;
  color: #0c3483;
  font-weight: bold;
}

.system-desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.login-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #0f5298 inset;
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #2cb5e8 inset, 0 0 15px rgba(44, 181, 232, 0.3);
}

.login-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  background: linear-gradient(135deg, #0c3483 0%, #2cb5e8 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: linear-gradient(135deg, #0f5298 0%, #2cb5e8 100%);
  box-shadow: 0 0 20px rgba(44, 181, 232, 0.5);
  transform: translateY(-2px);
}

.login-tips {
  margin-top: 20px;
  text-align: center;
  color: #909399;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.login-footer {
  margin-top: 20px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}
</style>
