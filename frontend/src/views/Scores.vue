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
          <el-option v-for="s in semesters" :key="s.id" :label="s.name" :value="s.name" />
        </el-select>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          录入成绩
        </el-button>
        <el-button type="success" @click="showBatchDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button type="info" @click="handleOpenAnalysis">
          <el-icon><DataAnalysis /></el-icon>
          成绩分析
        </el-button>
        <el-button type="success" @click="handleExportScores" :loading="exportLoading">
          <el-icon><Download /></el-icon>
          导出成绩
        </el-button>
      </div>
    </div>

    <div class="statistics-card" v-if="statisticsData">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均分</div>
            <div class="stat-value">{{ statisticsData.average.toFixed(1) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">最高分</div>
            <div class="stat-value success">{{ statisticsData.max }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">最低分</div>
            <div class="stat-value danger">{{ statisticsData.min }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">及格率</div>
            <div class="stat-value">{{ statisticsData.passRate }}%</div>
          </div>
        </el-col>
      </el-row>
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
        <el-table-column prop="exam_type" label="考试类型" width="120" />
        <el-table-column prop="exam_date" label="考试日期" width="120">
          <template #default="{ row }">
            {{ row.exam_date ? formatDate(row.exam_date) : '-' }}
          </template>
        </el-table-column>
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
          <el-select v-model="form.exam_type" style="width: 100%;" filterable allow-create placeholder="选择或输入考试类型">
            <el-option label="期中考试" value="期中考试" />
            <el-option label="期末考试" value="期末考试" />
            <el-option label="月考" value="月考" />
            <el-option label="测验" value="测验" />
            <el-option label="模拟考试" value="模拟考试" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试日期" prop="exam_date">
          <el-date-picker
            v-model="form.exam_date"
            type="datetime"
            placeholder="选择考试日期"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="学期" prop="semester">
          <el-select v-model="form.semester" style="width: 100%;" placeholder="选择学期">
            <el-option v-for="s in semesters" :key="s.id" :label="s.name" :value="s.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchDialog" title="批量导入成绩" width="800px">
      <div style="margin-bottom: 15px;">
        <el-alert title="导入说明" type="info" :closable="false">
          <ol style="margin: 10px 0 0 20px; padding: 0;">
            <li>请先<strong>下载模板</strong>获取Excel文件</li>
            <li>按照模板格式填写成绩信息</li>
            <li>学号和科目必须正确填写</li>
            <li>成绩必须在0-100之间</li>
            <li>选择班级、科目、学期后，上传文件并点击"导入"</li>
          </ol>
        </el-alert>
      </div>
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="选择班级">
          <el-select v-model="batchForm.class_id" placeholder="选择班级" style="width: 100%;">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择科目">
          <el-select v-model="batchForm.subject_id" placeholder="选择科目" style="width: 100%;">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试类型">
          <el-select v-model="batchForm.exam_type" style="width: 100%;">
            <el-option label="期中考试" value="期中考试" />
            <el-option label="期末考试" value="期末考试" />
            <el-option label="月考" value="月考" />
            <el-option label="测验" value="测验" />
            <el-option label="模拟考试" value="模拟考试" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试日期">
          <el-date-picker
            v-model="batchForm.exam_date"
            type="date"
            placeholder="选择考试日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="选择学期">
          <el-select v-model="batchForm.semester" placeholder="选择学期" style="width: 100%;">
            <el-option v-for="s in semesters" :key="s.id" :label="s.name" :value="s.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            accept=".csv,.xlsx"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击选择文件</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持CSV和Excel文件（.csv, .xlsx）</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item v-if="batchForm.scoreData">
          <el-input
            v-model="batchForm.scoreData"
            type="textarea"
            :rows="6"
            placeholder="预览数据"
            readonly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="downloadTemplate">下载模板</el-button>
        <el-button @click="showBatchDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchImport" :loading="batchLoading">导入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAnalysisDialog" title="成绩分析" width="90%" top="5vh">
      <el-tabs v-model="activeAnalysisTab">
        <el-tab-pane label="成绩分布" name="distribution">
          <div class="analysis-container">
            <div ref="distributionChartRef" class="chart-container"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="各科目对比" name="subjects">
          <div class="analysis-container">
            <div ref="subjectsChartRef" class="chart-container"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="学生排名" name="ranking">
          <div class="analysis-container">
            <el-table :data="studentRanking" size="small" border stripe>
              <el-table-column prop="rank" label="排名" width="80" />
              <el-table-column prop="student_name" label="学生姓名" />
              <el-table-column prop="average_score" label="平均分" />
              <el-table-column prop="total_score" label="总分" />
              <el-table-column prop="subject_count" label="科目数" />
            </el-table>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="成绩详情" name="details">
          <div class="analysis-container">
            <el-row :gutter="20" class="detail-stats">
              <el-col :span="6">
                <el-statistic title="优秀（90分以上）" :value="scoreDistribution.excellent" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="良好（80-89分）" :value="scoreDistribution.good" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="及格（60-79分）" :value="scoreDistribution.pass" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="不及格（60分以下）" :value="scoreDistribution.fail" />
              </el-col>
            </el-row>
            <div ref="trendChartRef" class="chart-container"></div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled, Upload, DataAnalysis, Download } from '@element-plus/icons-vue'
import api from '@/api'
import * as XLSX from 'xlsx'
import * as echarts from 'echarts'

const router = useRouter()

const scores = ref([])
const classes = ref([])
const subjects = ref([])
const semesters = ref([])
const students = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const showBatchDialog = ref(false)
const batchLoading = ref(false)
const uploadRef = ref(null)

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
  exam_type: '期中考试',
  exam_date: null,
  semester: ''
})

const batchForm = reactive({
  class_id: null,
  subject_id: null,
  exam_type: '期中考试',
  exam_date: null,
  semester: '',
  scoreData: '',
  scoreList: []
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

const loadSemesters = async () => {
  const data = await api.semesters.list()
  semesters.value = data || []
}

const loadStudents = async () => {
  const data = await api.students.list({ page_size: 1000 })
  students.value = (data?.data || []).filter(s => s.id)
}

const showAnalysisDialog = ref(false)
const activeAnalysisTab = ref('distribution')
const distributionChartRef = ref(null)
const subjectsChartRef = ref(null)
const trendChartRef = ref(null)
const studentRanking = ref([])
const exportLoading = ref(false)
const scoreDistribution = reactive({
  excellent: 0,
  good: 0,
  pass: 0,
  fail: 0
})

const statisticsData = ref(null)

const calculateStatistics = () => {
  if (!scores.value || scores.value.length === 0) {
    statisticsData.value = null
    return
  }
  
  const scores_list = scores.value.map(s => s.score).filter(s => typeof s === 'number')
  if (scores_list.length === 0) {
    statisticsData.value = null
    return
  }
  
  const average = scores_list.reduce((a, b) => a + b, 0) / scores_list.length
  const max = Math.max(...scores_list)
  const min = Math.min(...scores_list)
  const passCount = scores_list.filter(s => s >= 60).length
  const passRate = ((passCount / scores_list.length) * 100).toFixed(1)
  
  statisticsData.value = {
    average,
    max,
    min,
    passRate
  }
  
  scoreDistribution.excellent = scores_list.filter(s => s >= 90).length
  scoreDistribution.good = scores_list.filter(s => s >= 80 && s < 90).length
  scoreDistribution.pass = scores_list.filter(s => s >= 60 && s < 80).length
  scoreDistribution.fail = scores_list.filter(s => s < 60).length
}

const handleOpenAnalysis = () => {
  router.push('/analysis')
}

const handleExportScores = async () => {
  try {
    exportLoading.value = true
    
    const data = await api.scores.list({
      class_id: filterClassId.value || undefined,
      subject_id: filterSubjectId.value || undefined,
      semester: filterSemester.value || undefined,
      page: 1,
      page_size: 1000
    })
    
    const scoresList = data?.data || []
    
    if (scoresList.length === 0) {
      ElMessage.warning('没有成绩数据可导出')
      exportLoading.value = false
      return
    }
    
    const exportData = [
      ['学生姓名', '科目', '成绩', '考试类型', '考试日期', '学期']
    ]
    
    scoresList.forEach(s => {
      exportData.push([
        s.student_name || '',
        s.subject_name || '',
        s.score || '',
        s.exam_type || '',
        s.exam_date ? s.exam_date.substring(0, 10) : '',
        s.semester || ''
      ])
    })
    
    const ws = XLSX.utils.aoa_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '成绩单')
    
    const timestamp = new Date().toISOString().slice(0, 10)
    XLSX.writeFile(wb, `成绩单_${timestamp}.xlsx`)
    
    exportLoading.value = false
    ElMessage.success(`成功导出 ${scoresList.length} 条成绩记录`)
  } catch (e) {
    exportLoading.value = false
    console.error('导出成绩失败:', e)
    ElMessage.error('导出成绩失败')
  }
}

const initDistributionChart = () => {
  if (!distributionChartRef.value || !scores.value.length) return
  
  const chart = echarts.init(distributionChartRef.value)
  const distribution = [0, 0, 0, 0, 0]
  
  scores.value.forEach(s => {
    const score = parseFloat(s.score)
    if (isNaN(score)) return
    if (score >= 90) distribution[0]++
    else if (score >= 80) distribution[1]++
    else if (score >= 70) distribution[2]++
    else if (score >= 60) distribution[3]++
    else distribution[4]++
  })
  
  const option = {
    title: {
      text: '成绩分布直方图',
      left: 'center',
      top: 10
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '80px',
      bottom: '60px'
    },
    xAxis: {
      type: 'category',
      data: ['90-100分', '80-89分', '70-79分', '60-69分', '60分以下']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: distribution,
      type: 'bar',
      itemStyle: {
        color: (params) => {
          const colors = ['#67C23A', '#409EFF', '#E6A23C', '#F56C6C', '#909399']
          return colors[params.dataIndex]
        }
      },
      label: {
        show: true,
        position: 'top'
      }
    }]
  }
  
  chart.setOption(option)
}

const initSubjectsChart = () => {
  if (!subjectsChartRef.value || !scores.value.length) return
  
  const chart = echarts.init(subjectsChartRef.value)
  const subjectScores = {}
  
  scores.value.forEach(s => {
    const subject = s.subject_name || '未知科目'
    const score = parseFloat(s.score)
    if (!subjectScores[subject]) {
      subjectScores[subject] = []
    }
    if (!isNaN(score)) {
      subjectScores[subject].push(score)
    }
  })
  
  const subjects = Object.keys(subjectScores)
  const averages = subjects.map(s => {
    const scores_list = subjectScores[s]
    if (scores_list.length === 0) return 0
    const avg = scores_list.reduce((a, b) => a + b, 0) / scores_list.length
    return parseFloat(avg.toFixed(1))
  })
  
  const option = {
    title: {
      text: '各科目平均分对比',
      left: 'center',
      top: 10
    },
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '80px',
      bottom: '60px'
    },
    xAxis: {
      type: 'category',
      data: subjects,
      axisLabel: {
        interval: 0,
        rotate: subjects.length > 5 ? 30 : 0,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [{
      data: averages,
      type: 'bar',
      itemStyle: {
        color: '#409EFF'
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}'
      }
    }]
  }
  
  chart.setOption(option)
}

const initTrendChart = () => {
  if (!trendChartRef.value || !scores.value.length) return
  
  const chart = echarts.init(trendChartRef.value)
  
  const examDates = [...new Set(scores.value.map(s => s.exam_date))].filter(d => d).sort()
  
  const subjectScores = {}
  scores.value.forEach(s => {
    const subject = s.subject_name || '未知科目'
    const score = parseFloat(s.score)
    if (!subjectScores[subject]) {
      subjectScores[subject] = []
    }
    if (!isNaN(score)) {
      subjectScores[subject].push({
        date: s.exam_date,
        score: score
      })
    }
  })
  
  const series = Object.keys(subjectScores).map(subject => ({
    name: subject,
    type: 'line',
    data: examDates.map(date => {
      const record = subjectScores[subject].find(r => r.date === date)
      return record ? record.score : null
    }),
    smooth: true
  }))
  
  const option = {
    title: {
      text: '成绩趋势变化',
      left: 'center',
      top: 10
    },
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '80px',
      bottom: '80px'
    },
    legend: {
      data: Object.keys(subjectScores),
      bottom: 10
    },
    xAxis: {
      type: 'category',
      data: examDates.map(d => d ? d.substring(0, 10) : '')
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series
  }
  
  chart.setOption(option)
}

const calculateStudentRanking = () => {
  const studentScores = {}
  
  scores.value.forEach(s => {
    if (!studentScores[s.student_name]) {
      studentScores[s.student_name] = []
    }
    studentScores[s.student_name].push(s.score)
  })
  
  const rankings = Object.keys(studentScores).map(name => {
    const scores_list = studentScores[name]
    return {
      student_name: name,
      average_score: (scores_list.reduce((a, b) => a + b, 0) / scores_list.length).toFixed(1),
      total_score: scores_list.reduce((a, b) => a + b, 0),
      subject_count: scores_list.length
    }
  })
  
  rankings.sort((a, b) => b.average_score - a.average_score)
  
  studentRanking.value = rankings.map((r, index) => ({
    ...r,
    rank: index + 1
  }))
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
    scores.value = (data?.data || []).map(s => ({
      ...s,
      student_name: s.student_name || students.value.find(st => st.id === s.student_id)?.name || '',
      subject_name: s.subject_name || subjects.value.find(sub => sub.id === s.subject_id)?.name || ''
    }))
    total.value = data?.total || scores.value.length
    
    calculateStatistics()
    calculateStudentRanking()
  } catch (e) {
    scores.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleFileChange = (uploadFile) => {
  const fileName = uploadFile.name
  const fileExt = fileName.substring(fileName.lastIndexOf('.')).toLowerCase()

  if (fileExt === '.xlsx' || fileExt === '.xls') {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })

        if (jsonData.length > 1) {
          const header = jsonData[0].map(h => String(h).trim())
          const rows = jsonData.slice(1).filter(row => row.some(cell => cell !== undefined && cell !== null && cell !== ''))

          batchForm.scoreList = rows.map(row => {
                const getValue = (index) => row[index] !== undefined ? String(row[index]).trim() : ''
                const studentNo = getValue(header.indexOf('学号'))

                return {
                  student_no: studentNo,
                  score: parseFloat(getValue(header.indexOf('成绩'))) || 0
                }
              }).filter(s => s.student_no)

          const csvLines = rows.map(row => {
            return header.map((col, i) => {
              const value = row[i] !== undefined ? String(row[i]) : ''
              return value
            }).join(',')
          })
          batchForm.scoreData = csvLines.join('\n')

          ElMessage.success(`Excel文件解析成功，共${batchForm.scoreList.length}条数据`)
        } else {
          ElMessage.warning('Excel文件中没有数据')
        }
      } catch (err) {
        console.error('Excel解析失败:', err)
        ElMessage.error('Excel文件解析失败')
      }
    }
    reader.readAsArrayBuffer(uploadFile.raw)
  } else {
    ElMessage.warning('请上传Excel文件（.xlsx）')
  }
}

const downloadTemplate = () => {
  const data = [
    ['学号', '成绩'],
    ['1', '85'],
    ['2', '90'],
    ['3', '78']
  ]

  const ws = XLSX.utils.aoa_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '成绩信息')

  XLSX.writeFile(wb, '成绩导入模板.xlsx')
}

const handleBatchImport = async () => {
  if (!batchForm.class_id) {
    ElMessage.warning('请选择班级')
    return
  }
  if (!batchForm.subject_id) {
    ElMessage.warning('请选择科目')
    return
  }
  if (!batchForm.semester) {
    ElMessage.warning('请选择学期')
    return
  }
  if (!batchForm.scoreList || batchForm.scoreList.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }

  batchLoading.value = true

  const scoresList = batchForm.scoreList.map(s => ({
    student_no: s.student_no,
    class_id: batchForm.class_id,
    subject_id: batchForm.subject_id,
    score: s.score,
    exam_type: batchForm.exam_type || '期中考试',
    exam_date: batchForm.exam_date,
    semester: batchForm.semester
  }))

  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/scores/batch', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json; charset=utf-8'
      },
      body: JSON.stringify({ scores: scoresList })
    })

    const result = await response.json()

    if (result.success > 0) {
      ElMessage.success(`成功导入 ${result.success} 条成绩`)
    }
    if (result.failed > 0) {
      ElMessage.warning(`导入失败 ${result.failed} 条`)
    }
    if (result.errors && result.errors.length > 0) {
      console.log('导入错误:', result.errors)
      ElMessage.warning(`错误详情: ${result.errors.slice(0, 5).join(', ')}${result.errors.length > 5 ? '...' : ''}`)
    }

    showBatchDialog.value = false
    batchForm.scoreData = ''
    batchForm.scoreList = []
    batchForm.class_id = null
    batchForm.subject_id = null
    batchForm.semester = ''
    loadScores()
  } catch (e) {
    ElMessage.error('批量导入失败')
  } finally {
    batchLoading.value = false
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
    exam_type: '期中考试',
    exam_date: null,
    semester: semesters.value[0]?.name || ''
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
    exam_date: row.exam_date,
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
    const data = {
      student_id: form.student_id,
      subject_id: form.subject_id,
      class_id: students.value.find(s => s.id === form.student_id)?.class_id || form.class_id,
      score: form.score,
      exam_type: form.exam_type,
      exam_date: form.exam_date,
      semester: form.semester
    }
    
    if (isEdit.value) {
      await api.scores.update(editingId.value, {
        score: form.score,
        exam_type: form.exam_type,
        exam_date: form.exam_date,
        semester: form.semester
      })
      ElMessage.success('修改成功')
    } else {
      await api.scores.create(data)
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

watch(() => showAnalysisDialog.value, (newVal) => {
  if (newVal) {
    nextTick(() => {
      initDistributionChart()
      initSubjectsChart()
      initTrendChart()
    })
  }
})

watch(() => activeAnalysisTab.value, (newVal) => {
  if (newVal) {
    nextTick(() => {
      if (newVal === 'distribution') {
        initDistributionChart()
      } else if (newVal === 'subjects') {
        initSubjectsChart()
      } else if (newVal === 'details') {
        initTrendChart()
      }
    })
  }
})

onMounted(async () => {
  await Promise.all([loadClasses(), loadSubjects(), loadSemesters(), loadStudents()])
  loadScores()
})
</script>

<style scoped>
.scores {
  padding: 20px;
}

.statistics-card {
  background: white;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stat-value.success {
  color: #67C23A;
}

.stat-value.danger {
  color: #F56C6C;
}

.analysis-container {
  padding: 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}

.detail-stats {
  margin-bottom: 30px;
}
</style>
