<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span><el-icon><Setting /></el-icon> 系统设置</span>
        </div>
      </template>

      <el-form :model="form" label-width="120px" v-loading="loading">
        <el-form-item label="系统名称">
          <el-input v-model="form.system_name" placeholder="请输入系统名称" />
        </el-form-item>

        <el-form-item label="系统简介">
          <el-input v-model="form.system_intro" type="textarea" :rows="3" placeholder="请输入系统简介" />
        </el-form-item>

        <el-form-item label="系统Logo">
          <div class="logo-upload">
            <el-input v-model="form.system_logo" placeholder="请输入Logo图片URL">
              <template #append>
                <el-button @click="uploadLogo">上传</el-button>
              </template>
            </el-input>
            <div class="logo-preview" v-if="form.system_logo">
              <img :src="form.system_logo" alt="Logo" />
            </div>
            <div class="logo-tip">支持在线图片URL，建议尺寸 200x60</div>
          </div>
        </el-form-item>

        <el-form-item label="Bing 每日一图">
          <el-switch
            v-model="form.use_bing_background"
            active-text="启用"
            inactive-text="禁用"
          />
          <div class="form-tip">启用后，登录页面将自动使用 Bing 每日一图作为背景</div>
        </el-form-item>

        <el-form-item label="登录背景图">
          <div class="background-upload">
            <el-input v-model="form.login_background" placeholder="请输入背景图片URL" :disabled="form.use_bing_background">
              <template #append>
                <el-button @click="uploadBackground" :disabled="form.use_bing_background">上传</el-button>
              </template>
            </el-input>
            <div class="background-preview" v-if="form.login_background && !form.use_bing_background">
              <img :src="form.login_background" alt="背景图" />
            </div>
            <div class="background-tip" v-if="!form.use_bing_background">支持在线图片URL，建议尺寸 1920x1080</div>
            <div class="background-tip" v-else>已启用 Bing 每日一图，自定义背景将被忽略</div>
          </div>
        </el-form-item>

        <el-form-item label="版权信息">
          <el-input v-model="form.copyright" placeholder="请输入版权信息" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="saving">
            <el-icon><Select /></el-icon> 保存设置
          </el-button>
          <el-button @click="resetSettings">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="preview-card">
      <template #header>
        <span><el-icon><View /></el-icon> 登录页面预览</span>
      </template>
      <div class="login-preview">
        <div class="preview-background" :style="backgroundStyle">
          <div class="preview-login-box">
            <div class="preview-logo" v-if="form.system_logo">
              <img :src="form.system_logo" alt="Logo" />
            </div>
            <h2 class="preview-title">{{ form.system_name }}</h2>
            <p class="preview-intro">{{ form.system_intro }}</p>
            <el-input placeholder="用户名" disabled />
            <el-input placeholder="密码" type="password" disabled style="margin-top: 10px" />
            <el-button type="primary" style="width: 100%; margin-top: 15px" disabled>登录</el-button>
          </div>
          <div class="preview-footer">{{ form.copyright }}</div>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="uploadDialogVisible" title="上传图片" width="500px">
      <el-form>
        <el-form-item label="图片URL">
          <el-input v-model="imageUrl" placeholder="请输入图片URL" />
        </el-form-item>
        <el-form-item label="或上传文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            accept="image/*"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽图片到此处或<em>点击上传</em></div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmUpload">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, Select, Refresh, View, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const loading = ref(false)
const saving = ref(false)
const uploadDialogVisible = ref(false)
const imageUrl = ref('')
const currentUploadField = ref('')

const form = ref({
  system_name: 'DD-CLASS 班级管理系统',
  login_background: '',
  system_logo: '',
  system_intro: '一个现代化的班级管理系统',
  copyright: '© 2024 DD-CLASS',
  use_bing_background: true
})

const originalForm = ref({})

const backgroundStyle = computed(() => {
  if (form.value.login_background) {
    return {
      backgroundImage: `url(${form.value.login_background})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  }
})

const fetchSettings = async () => {
  loading.value = true
  try {
    const res = await api.get('/settings/all')
    const settingsData = {}
    res.data.forEach(item => {
      settingsData[item.setting_key] = item.setting_value
    })
    form.value = {
      system_name: settingsData.system_name || 'DD-CLASS 班级管理系统',
      login_background: settingsData.login_background || '',
      system_logo: settingsData.system_logo || '',
      system_intro: settingsData.system_intro || '一个现代化的班级管理系统',
      copyright: settingsData.copyright || '© 2024 DD-CLASS',
      use_bing_background: settingsData.use_bing_background === 'true'
    }
    originalForm.value = { ...form.value }
  } catch (e) {
    ElMessage.error('获取设置失败')
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await api.post('/settings/batch-update', form.value)
    ElMessage.success('设置保存成功！')
    originalForm.value = { ...form.value }
  } catch (e) {
    ElMessage.error('保存失败：' + (e.response?.data?.detail || '未知错误'))
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  form.value = { ...originalForm.value }
}

const uploadLogo = () => {
  currentUploadField.value = 'system_logo'
  imageUrl.value = form.value.system_logo
  uploadDialogVisible.value = true
}

const uploadBackground = () => {
  currentUploadField.value = 'login_background'
  imageUrl.value = form.value.login_background
  uploadDialogVisible.value = true
}

const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    imageUrl.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const confirmUpload = () => {
  if (!imageUrl.value) {
    ElMessage.warning('请输入图片URL或上传图片')
    return
  }
  form.value[currentUploadField.value] = imageUrl.value
  uploadDialogVisible.value = false
  ElMessage.success('图片已添加')
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

.logo-upload, .background-upload {
  width: 100%;
}

.logo-preview {
  margin-top: 15px;
}

.logo-preview img {
  max-width: 200px;
  max-height: 60px;
}

.background-preview {
  margin-top: 15px;
}

.background-preview img {
  max-width: 400px;
  max-height: 200px;
  border-radius: 8px;
}

.logo-tip, .background-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.preview-card {
  margin-top: 20px;
}

.login-preview {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
}

.preview-background {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.preview-login-box {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 12px;
  width: 350px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.preview-logo {
  margin-bottom: 20px;
}

.preview-logo img {
  max-width: 200px;
  max-height: 60px;
}

.preview-title {
  margin: 10px 0;
  color: #333;
}

.preview-intro {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.preview-footer {
  position: absolute;
  bottom: 20px;
  color: white;
  font-size: 12px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>
