<template>
  <div class="notification-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span><el-icon><Bell /></el-icon> 通知管理</span>
          <div class="header-actions">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="badge">
              <el-button @click="markAllRead" :disabled="unreadCount === 0">全部标为已读</el-button>
            </el-badge>
            <el-button type="primary" @click="openAddDialog" v-if="!isStudent">
              <el-icon><Plus /></el-icon> 发布通知
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="notifications" v-loading="loading" stripe @row-click="viewNotification">
        <el-table-column width="50">
          <template #default="{ row }">
            <el-tag v-if="row.is_pinned" type="warning" size="small">置顶</el-tag>
            <span v-else-if="!row.is_read" class="unread-dot"></span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="通知标题" min-width="180">
          <template #default="{ row }">
            <span :class="{ 'unread-title': !row.is_read }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="class_name" label="范围" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.class_name" type="info" size="small">{{ row.class_name }}</el-tag>
            <el-tag v-else type="success" size="small">全校</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">{{ getPriorityText(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="发布人" width="100" />
        <el-table-column prop="created_at" label="发布时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" v-if="!isStudent">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click.stop="editNotification(row)">编辑</el-button>
            <el-button size="small" type="danger" @click.stop="deleteNotification(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchNotifications"
        @current-change="fetchNotifications"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="通知标题" required>
          <el-input v-model="form.title" placeholder="请输入通知标题" />
        </el-form-item>
        <el-form-item label="通知范围">
          <el-select v-model="form.class_id" placeholder="选择班级（不选则为全校通知）" clearable :disabled="!isAdmin && !canSelectClass">
            <el-option label="全校通知" :value="null" />
            <el-option v-for="cls in classes" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
          <div class="form-tip" v-if="!isAdmin">班主任只能发布本班通知</div>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority" placeholder="请选择优先级">
            <el-option label="普通" value="normal" />
            <el-option label="重要" value="important" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.is_pinned" />
        </el-form-item>
        <el-form-item label="通知内容">
          <el-input v-model="form.content" type="textarea" :rows="6" placeholder="请输入通知内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">{{ dialogMode === 'add' ? '发布' : '保存' }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="通知详情" width="600px">
      <el-descriptions :column="2" border v-if="currentNotification">
        <el-descriptions-item label="通知标题" :span="2">{{ currentNotification.title }}</el-descriptions-item>
        <el-descriptions-item label="通知范围">
          <el-tag v-if="currentNotification.class_name" type="info">{{ currentNotification.class_name }}</el-tag>
          <el-tag v-else type="success">全校</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(currentNotification.priority)" size="small">{{ getPriorityText(currentNotification.priority) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="置顶">{{ currentNotification.is_pinned ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="发布人">{{ currentNotification.creator_name }}</el-descriptions-item>
        <el-descriptions-item label="发布时间">{{ formatDate(currentNotification.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="通知内容" :span="2">{{ currentNotification.content || '无' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const userStore = useUserStore()
const isStudent = computed(() => userStore.userInfo?.role === 'student')
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')
const canSelectClass = computed(() => ['class_teacher', 'teacher'].includes(userStore.userInfo?.role))

const notifications = ref([])
const classes = ref([])
const loading = ref(false)
const submitting = ref(false)
const total = ref(0)
const unreadCount = ref(0)
const page = ref(1)
const pageSize = ref(20)

const dialogVisible = ref(false)
const dialogMode = ref('add')
const dialogTitle = computed(() => dialogMode.value === 'add' ? '发布通知' : '编辑通知')

const detailVisible = ref(false)
const currentNotification = ref(null)

const form = ref({
  title: '',
  content: '',
  priority: 'normal',
  is_pinned: false,
  class_id: null
})

const fetchClasses = async () => {
  try {
    const res = await api.get('/classes')
    classes.value = res.data
  } catch (e) {
    console.error('获取班级失败', e)
  }
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const res = await api.get('/notifications', {
      params: {
        page: page.value,
        page_size: pageSize.value
      }
    })
    notifications.value = res.data.data
    total.value = res.data.total
    unreadCount.value = res.data.unread_count
  } catch (e) {
    ElMessage.error('获取通知列表失败')
  } finally {
    loading.value = false
  }
}

const markAllRead = async () => {
  try {
    await api.post('/notifications/mark-all-read')
    ElMessage.success('已全部标为已读')
    fetchNotifications()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const openAddDialog = () => {
  dialogMode.value = 'add'
  form.value = {
    title: '',
    content: '',
    priority: 'normal',
    is_pinned: false,
    class_id: isAdmin.value ? null : userStore.userInfo?.class_id
  }
  dialogVisible.value = true
}

const editNotification = async (row) => {
  try {
    const res = await api.get(`/notifications/${row.id}`)
    currentNotification.value = res.data
    dialogMode.value = 'edit'
    form.value = {
      title: res.data.title,
      content: res.data.content,
      priority: res.data.priority,
      is_pinned: res.data.is_pinned,
      class_id: res.data.class_id
    }
    dialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取通知详情失败')
  }
}

const submitForm = async () => {
  if (!form.value.title) {
    ElMessage.warning('请填写通知标题')
    return
  }
  
  submitting.value = true
  try {
    if (dialogMode.value === 'add') {
      await api.post('/notifications', form.value)
      ElMessage.success('通知发布成功')
    } else {
      await api.put(`/notifications/${currentNotification.value.id}`, form.value)
      ElMessage.success('通知更新成功')
    }
    
    dialogVisible.value = false
    fetchNotifications()
  } catch (e) {
    ElMessage.error('操作失败：' + (e.response?.data?.detail || '未知错误'))
  } finally {
    submitting.value = false
  }
}

const viewNotification = async (row) => {
  try {
    const res = await api.get(`/notifications/${row.id}`)
    currentNotification.value = res.data
    
    if (!res.data.is_read) {
      await api.post(`/notifications/${row.id}/read`)
    }
    
    detailVisible.value = true
    
    setTimeout(() => {
      fetchNotifications()
    }, 100)
  } catch (e) {
    ElMessage.error('获取通知详情失败')
  }
}

const deleteNotification = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个通知吗？', '提示', { type: 'warning' })
    await api.delete(`/notifications/${row.id}`)
    ElMessage.success('删除成功')
    fetchNotifications()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getPriorityType = (priority) => {
  const map = { normal: '', important: 'warning', urgent: 'danger' }
  return map[priority] || ''
}

const getPriorityText = (priority) => {
  const map = { normal: '普通', important: '重要', urgent: '紧急' }
  return map[priority] || '普通'
}

const formatDate = (date) => {
  if (!date) return '无'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchClasses()
  fetchNotifications()
})
</script>

<style scoped>
.notification-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-size: 18px; font-weight: bold; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.badge { margin-right: 10px; }
.unread-dot { display: inline-block; width: 8px; height: 8px; background: #409eff; border-radius: 50%; }
.unread-title { font-weight: bold; }
.form-tip { font-size: 12px; color: #909399; margin-top: 4px; }
</style>
