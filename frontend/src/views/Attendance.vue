<template>
  <div class="attendance">
    <div class="page-header">
      <h1 class="page-title">考勤管理</h1>
      <div>
        <el-select v-model="filterClassId" placeholder="选择班级" clearable style="width: 150px; margin-right: 10px;" @change="loadAttendances">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-date-picker
          v-model="filterDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 150px; margin-right: 10px;"
          @change="loadAttendances"
        />
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          录入考勤
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">总考勤次数</div>
          <div class="stat-value">{{ stats.total }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">出勤</div>
          <div class="stat-value" style="color: #67c23a;">{{ stats.present }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">缺勤</div>
          <div class="stat-value" style="color: #f56c6c;">{{ stats.absent }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-label">出勤率</div>
          <div class="stat-value" style="color: #409eff;">{{ stats.attendance_rate }}%</div>
        </div>
      </el-col>
    </el-row>

    <div class="table-container">
      <el-table :data="attendances" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="student_name" label="学生" />
        <el-table-column prop="date" label="日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑考勤' : '录入考勤'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="form.student_id" placeholder="选择学生" style="width: 100%;" filterable>
            <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.class_name})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="form.date"
            type="datetime"
            placeholder="选择日期"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="present">出勤</el-radio>
            <el-radio label="absent">缺勤</el-radio>
            <el-radio label="late">迟到</el-radio>
            <el-radio label="leave">请假</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const attendances = ref([])
const classes = ref([])
const students = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const filterClassId = ref(null)
const filterDate = ref(null)
const stats = reactive({
  total: 0,
  present: 0,
  absent: 0,
  late: 0,
  leave: 0,
  attendance_rate: 0
})

const form = reactive({
  student_id: null,
  class_id: null,
  date: null,
  status: 'present',
  remark: ''
})

const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const getStatusType = (status) => {
  const map = { present: 'success', absent: 'danger', late: 'warning', leave: 'info' }
  return map[status] || ''
}

const getStatusText = (status) => {
  const map = { present: '出勤', absent: '缺勤', late: '迟到', leave: '请假' }
  return map[status] || status
}

const loadClasses = async () => {
  const data = await api.classes.list()
  classes.value = (data || []).filter(c => c.id)
}

const loadStudents = async () => {
  const data = await api.students.list({ page_size: 1000 })
  students.value = (data || []).filter(s => s.id)
}

const loadAttendances = async () => {
  loading.value = true
  try {
    const params = { class_id: filterClassId.value }
    if (filterDate.value) {
      params.start_date = filterDate.value + 'T00:00:00'
      params.end_date = filterDate.value + 'T23:59:59'
    }
    const data = await api.attendance.list(params)
    attendances.value = data || []
    
    if (filterClassId.value) {
      const statsData = await api.attendance.getClassStats(filterClassId.value, {
        start_date: params.start_date,
        end_date: params.end_date
      })
      Object.assign(stats, statsData)
    } else {
      stats.total = attendances.value.length
      let present = 0
      attendances.value.forEach(a => {
        if (a.status === 'present') present++
      })
      stats.present = present
      stats.attendance_rate = stats.total > 0 ? Math.round(present / stats.total * 100) : 0
    }
  } catch (e) {
    attendances.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    student_id: null,
    class_id: filterClassId.value || classes.value[0]?.id,
    date: new Date().toISOString(),
    status: 'present',
    remark: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    student_id: row.student_id,
    class_id: row.class_id,
    date: row.date,
    status: row.status,
    remark: row.remark
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该考勤记录吗?', '提示', { type: 'warning' })
    await api.attendance.delete(row.id)
    ElMessage.success('删除成功')
    loadAttendances()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  try {
    const data = {
      ...form,
      class_id: students.value.find(s => s.id === form.student_id)?.class_id || form.class_id
    }
    
    if (isEdit.value) {
      await api.attendance.update(editingId.value, {
        status: form.status,
        remark: form.remark
      })
      ElMessage.success('修改成功')
    } else {
      await api.attendance.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadAttendances()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(async () => {
  await Promise.all([loadClasses(), loadStudents()])
  loadAttendances()
})
</script>

<style scoped>
.attendance {
  padding: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
</style>
