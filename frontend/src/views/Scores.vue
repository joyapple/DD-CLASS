<template>
  <div class="scores">
    <div class="page-header">
      <h1 class="page-title">成绩管理</h1>
      <div>
        <el-select v-model="filterClassId" placeholder="选择班级" clearable style="width: 150px; margin-right: 10px;" @change="loadScores">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="filterSubjectId" placeholder="选择科目" clearable style="width: 150px; margin-right: 10px;" @change="loadScores">
          <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="filterSemester" placeholder="选择学期" clearable style="width: 120px; margin-right: 10px;" @change="loadScores">
          <el-option label="2024-1" value="2024-1" />
          <el-option label="2024-2" value="2024-2" />
        </el-select>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          录入成绩
        </el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table :data="scores" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="student_name" label="学生" />
        <el-table-column prop="subject_name" label="科目" />
        <el-table-column prop="score" label="成绩" width="100">
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.score)">{{ row.score }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_type" label="考试类型" width="100" />
        <el-table-column prop="semester" label="学期" width="100" />
        <el-table-column prop="created_at" label="录入时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadScores"
        @current-change="loadScores"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑成绩' : '录入成绩'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="form.student_id" placeholder="选择学生" style="width: 100%;" filterable>
            <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.class_name})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="科目" prop="subject_id">
          <el-select v-model="form.subject_id" placeholder="选择科目" style="width: 100%;">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="成绩" prop="score">
          <el-input-number v-model="form.score" :min="0" :max="100" :step="0.5" />
        </el-form-item>
        <el-form-item label="考试类型" prop="exam_type">
          <el-select v-model="form.exam_type" style="width: 100%;">
            <el-option label="期中考试" value="midterm" />
            <el-option label="期末考试" value="final" />
            <el-option label="月考" value="monthly" />
            <el-option label="测验" value="quiz" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期" prop="semester">
          <el-select v-model="form.semester" style="width: 100%;">
            <el-option label="2024-1" value="2024-1" />
            <el-option label="2024-2" value="2024-2" />
          </el-select>
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

const scores = ref([])
const classes = ref([])
const subjects = ref([])
const students = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const filterClassId = ref(null)
const filterSubjectId = ref(null)
const filterSemester = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = reactive({
  student_id: null,
  subject_id: null,
  class_id: null,
  score: 0,
  exam_type: 'midterm',
  semester: '2024-1'
})

const rules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  subject_id: [{ required: true, message: '请选择科目', trigger: 'change' }],
  score: [{ required: true, message: '请输入成绩', trigger: 'blur' }],
  semester: [{ required: true, message: '请选择学期', trigger: 'change' }]
}

const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const loadClasses = async () => {
  const data = await api.classes.list()
  classes.value = (data || []).filter(c => c.id)
}

const loadSubjects = async () => {
  const data = await api.subjects.list()
  subjects.value = data || []
}

const loadStudents = async () => {
  const data = await api.students.list({ page_size: 1000 })
  students.value = (data || []).filter(s => s.id)
}

const loadScores = async () => {
  loading.value = true
  try {
    const data = await api.scores.list({
      class_id: filterClassId.value,
      subject_id: filterSubjectId.value,
      semester: filterSemester.value,
      page: page.value,
      page_size: pageSize.value
    })
    scores.value = data || []
  } catch (e) {
    scores.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    student_id: null,
    subject_id: null,
    class_id: filterClassId.value || classes.value[0]?.id,
    score: 0,
    exam_type: 'midterm',
    semester: '2024-1'
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    student_id: row.student_id,
    subject_id: row.subject_id,
    class_id: row.class_id,
    score: row.score,
    exam_type: row.exam_type,
    semester: row.semester
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该成绩吗?', '提示', { type: 'warning' })
    await api.scores.delete(row.id)
    ElMessage.success('删除成功')
    loadScores()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      await api.scores.update(editingId.value, {
        score: form.score,
        exam_type: form.exam_type,
        semester: form.semester
      })
      ElMessage.success('修改成功')
    } else {
      await api.scores.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadScores()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(async () => {
  await Promise.all([loadClasses(), loadSubjects(), loadStudents()])
  loadScores()
})
</script>

<style scoped>
.scores {
  padding: 20px;
}
</style>
