<template>
  <div class="subjects">
    <div class="page-header">
      <h1 class="page-title">科目管理</h1>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增科目
      </el-button>
    </div>

    <div class="table-container">
      <el-table :data="subjects" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="科目名称" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" title="新增科目" width="400px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="科目名称" prop="name">
          <el-input v-model="form.name" placeholder="如: 数学" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const subjects = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)

const form = reactive({
  name: ''
})

const rules = {
  name: [{ required: true, message: '请输入科目名称', trigger: 'blur' }]
}

const loadSubjects = async () => {
  const data = await api.subjects.list()
  subjects.value = data || []
}

const handleAdd = () => {
  form.name = ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该科目吗?', '提示', { type: 'warning' })
    await api.subjects.delete(row.id)
    ElMessage.success('删除成功')
    loadSubjects()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  try {
    await api.subjects.create(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadSubjects()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadSubjects()
})
</script>

<style scoped>
.subjects {
  padding: 20px;
}
</style>
