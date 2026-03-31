<template>
  <div class="score-analysis">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>成绩分析</span>
              <div class="header-actions">
                <el-select v-model="selectedClass" placeholder="选择班级" @change="onClassChange" style="width: 150px;">
                  <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
                </el-select>
                <el-select v-model="selectedStudent" placeholder="选择学生" @change="onStudentChange" style="width: 150px;" :disabled="!selectedClass">
                  <el-option v-for="s in students" :key="s.id" :label="s.name" :value="s.id" />
                </el-select>
                <el-select v-model="semester" placeholder="选择学期" @change="fetchAnalysis" style="width: 120px;">
                  <el-option label="全部" value="" />
                  <el-option label="2025-2" value="2025-2" />
                  <el-option label="2025-1" value="2025-1" />
                  <el-option label="2024-2" value="2024-2" />
                  <el-option label="2024-1" value="2024-1" />
                </el-select>
              </div>
            </div>
          </template>

          <div v-if="analysis" class="analysis-content">
            <el-row :gutter="20" class="stats-row">
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <div class="stat-number">{{ analysis.summary?.average_score || 0 }}</div>
                    <div class="stat-label">平均成绩</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <div class="stat-number">{{ analysis.summary?.max_score || 0 }}</div>
                    <div class="stat-label">最高成绩</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <div class="stat-number">{{ analysis.summary?.total_exams || 0 }}</div>
                    <div class="stat-label">考试次数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover">
                  <div class="stat-item">
                    <div class="stat-number">{{ analysis.summary?.rank_in_class || '-' }}/{{ analysis.summary?.class_student_count || 0 }}</div>
                    <div class="stat-label">班级排名</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>成绩趋势</template>
                  <div ref="trendChartRef" style="height: 300px;"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>科目分析</template>
                  <div ref="subjectChartRef" style="height: 300px;"></div>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="12">
                <el-card>
                  <template #header>科目对比</template>
                  <el-table :data="analysis.subject_analysis" style="width: 100%;">
                    <el-table-column prop="subject_name" label="科目" />
                    <el-table-column prop="avg_score" label="平均分" />
                    <el-table-column prop="max_score" label="最高分" />
                    <el-table-column prop="exam_count" label="考试次数" />
                  </el-table>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span style="color: #f56c6c;">⚠️ 薄弱科目</span>
                  </template>
                  <div v-if="analysis.weak_subjects?.length > 0">
                    <div v-for="item in analysis.weak_subjects" :key="item.subject_id" class="weak-item">
                      <span>{{ item.subject_name }}</span>
                      <span class="score">{{ item.avg_score }}分</span>
                      <span class="gap">低于平均 {{ item.gap }}分</span>
                    </div>
                  </div>
                  <el-empty v-else description="暂无薄弱科目" :image-size="60" />
                </el-card>
              </el-col>
            </el-row>
          </div>

          <el-empty v-else-if="!loading" description="请选择班级和学生" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;" v-if="selectedClass">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>班级成绩分析 - {{ getClassName() }}</span>
          </template>
          <div ref="classChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const trendChartRef = ref()
const subjectChartRef = ref()
const classChartRef = ref()

let trendChart = null
let subjectChart = null
let classChart = null

const classes = ref([])
const students = ref([])
const selectedClass = ref(null)
const selectedStudent = ref(null)
const semester = ref('')
const analysis = ref(null)
const loading = ref(false)
const classAnalysis = ref(null)

const fetchClasses = async () => {
  try {
    const data = await api.classes.list()
    classes.value = data
  } catch (e) {
    console.error('获取班级失败', e)
  }
}

const onClassChange = async () => {
  selectedStudent.value = null
  students.value = []
  analysis.value = null
  classAnalysis.value = null
  
  if (selectedClass.value) {
    try {
      const data = await api.students.list({ class_id: selectedClass.value, page: 1, page_size: 1000 })
      students.value = data.data || []
      
      const classData = await api.analytics.getClassAnalysis(selectedClass.value, { semester: semester.value })
      classAnalysis.value = classData
      nextTick(() => {
        initClassChart()
      })
    } catch (e) {
      console.error('获取学生失败', e)
    }
  }
}

const onStudentChange = () => {
  if (selectedStudent.value) {
    fetchAnalysis()
  } else {
    analysis.value = null
  }
}

const fetchAnalysis = async () => {
  if (!selectedStudent.value) return
  
  loading.value = true
  try {
    const data = await api.analytics.getStudentAnalysis(selectedStudent.value, { semester: semester.value })
    analysis.value = data
    nextTick(() => {
      initTrendChart()
      initSubjectChart()
    })
  } catch (e) {
    console.error('获取分析失败', e)
  } finally {
    loading.value = false
  }
}

const getClassName = () => {
  const cls = classes.value.find(c => c.id === selectedClass.value)
  return cls ? cls.name : ''
}

const initTrendChart = () => {
  if (!trendChartRef.value || !analysis.value?.trend) return
  
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)
  
  const trend = analysis.value.trend || []
  const dates = trend.map(t => t.date ? t.date.substring(5) : '')
  const scores = trend.map(t => t.score)
  
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', min: 0, max: 100 },
    series: [{
      data: scores,
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { width: 3 },
      itemStyle: { color: '#409eff' }
    }]
  })
}

const initSubjectChart = () => {
  if (!subjectChartRef.value || !analysis.value?.subject_analysis) return
  
  if (subjectChart) subjectChart.dispose()
  subjectChart = echarts.init(subjectChartRef.value)
  
  const subjects = analysis.value.subject_analysis || []
  const names = subjects.map(s => s.subject_name)
  const scores = subjects.map(s => s.avg_score)
  
  subjectChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', min: 0, max: 100 },
    series: [{
      data: scores,
      type: 'bar',
      itemStyle: {
        color: (params) => {
          const color = params.value >= 90 ? '#67c23a' : params.value >= 80 ? '#409eff' : params.value >= 60 ? '#e6a23c' : '#f56c6c'
          return color
        }
      },
      barWidth: '50%'
    }]
  })
}

const initClassChart = () => {
  if (!classChartRef.value || !classAnalysis.value?.score_distribution) return
  
  if (classChart) classChart.dispose()
  classChart = echarts.init(classChartRef.value)
  
  const dist = classAnalysis.value.score_distribution || {}
  
  classChart.setOption({
    tooltip: {},
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {c}人' },
      data: [
        { value: dist.excellent || 0, name: '优秀(≥90)', itemStyle: { color: '#67c23a' } },
        { value: dist.good || 0, name: '良好(80-89)', itemStyle: { color: '#409eff' } },
        { value: dist.average || 0, name: '中等(70-79)', itemStyle: { color: '#e6a23c' } },
        { value: dist.pass || 0, name: '及格(60-69)', itemStyle: { color: '#909399' } },
        { value: dist.fail || 0, name: '不及格(<60)', itemStyle: { color: '#f56c6c' } }
      ]
    }]
  })
}

onMounted(() => {
  fetchClasses()
})

watch(semester, () => {
  if (selectedClass.value) {
    api.analytics.getClassAnalysis(selectedClass.value, { semester: semester.value }).then(data => {
      classAnalysis.value = data
      nextTick(() => initClassChart())
    })
  }
  if (selectedStudent.value) {
    fetchAnalysis()
  }
})
</script>

<style scoped>
.score-analysis { padding: 20px; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px 0;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.chart-card {
  margin-bottom: 20px;
}

.weak-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #fef0f0;
  border-radius: 4px;
  margin-bottom: 8px;
}

.weak-item span:first-child {
  flex: 1;
  font-weight: 500;
}

.weak-item .score {
  color: #f56c6c;
  font-weight: bold;
  margin-right: 10px;
}

.weak-item .gap {
  color: #909399;
  font-size: 12px;
}
</style>
