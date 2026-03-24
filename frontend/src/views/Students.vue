<template>
  <div class="students">
    <div class="page-header">
      <h1 class="page-title">学生管理</h1>
      <div>
        <el-select v-model="filterClassId" placeholder="选择班级" clearable style="width: 180px; margin-right: 10px;">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-input v-model="searchName" placeholder="搜索学生姓名" style="width: 180px; margin-right: 10px;" clearable @change="loadStudents" />
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增学生
        </el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table :data="students" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="student_no" label="学号" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="parent_phone" label="家长电话" />
        <el-table-column label="操作" width="200">
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
        @size-change="loadStudents"
        @current-change="loadStudents"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学生' : '新增学生'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="学号" prop="student_no">
          <el-input v-model="form.student_no" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="选择班级" style="width: 100%;">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="家长电话" prop="parent_phone">
          <el-input v-model="form.parent_phone" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" />
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
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const students = ref([])
const classes = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const searchName = ref('')
const filterClassId = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = reactive({
  name: '',
  student_no: '',
  gender: 'male',
  class_id: null,
  phone: '',
  parent_phone: '',
  address: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }]
}

const loadClasses = async () => {
  const data = await api.classes.list()
  classes.value = (data || []).filter(c => c.id)
}

const loadStudents = async () => {
  loading.value = true
  try {
    const data = await api.students.list({
      class_id: filterClassId.value,
      name: searchName.value,
      page: page.value,
      page_size: pageSize.value
    })
    students.value = data || []
    total.value = (data || []).length
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    name: '',
    student_no: '',
    gender: 'male',
    class_id: classes.value[0]?.id || null,
    phone: '',
    parent_phone: '',
    address: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    student_no: row.student_no,
    gender: row.gender,
    class_id: row.class_id,
    phone: row.phone,
    parent_phone: row.parent_phone,
    address: row.address
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该学生吗?', '提示', { type: 'warning' })
    await api.students.delete(row.id)
    ElMessage.success('删除成功')
    loadStudents()
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
      await api.students.update(editingId.value, form)
      ElMessage.success('修改成功')
    } else {
      await api.students.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadStudents()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

watch([filterClassId], () => {
  page.value = 1
  loadStudents()
})

onMounted(async () => {
  await loadClasses()
  loadStudents()
})
</script>

<style scoped>
.students {
  padding: 20px;
}
</style>
