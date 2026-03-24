<template>
  <div class="rankings">
    <div class="page-header">
      <h1 class="page-title">班级排名</h1>
      <div>
        <el-select v-model="semester" placeholder="选择学期" @change="loadData" style="width: 150px; margin-right: 10px;">
          <el-option label="全部" value="" />
          <el-option label="2024-1" value="2024-1" />
          <el-option label="2024-2" value="2024-2" />
        </el-select>
        <el-select v-model="examType" placeholder="考试类型" clearable @change="loadData" style="width: 150px; margin-right: 10px;">
          <el-option label="期中考试" value="midterm" />
          <el-option label="期末考试" value="final" />
          <el-option label="月考" value="monthly" />
          <el-option label="测验" value="quiz" />
        </el-select>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="chart-card">
          <h3>班级平均分排名</h3>
          <el-table :data="classRankings" style="width: 100%">
            <el-table-column prop="rank" label="排名" width="80">
              <template #default="{ row }">
                <el-tag :type="getRankType(row.rank)">{{ row.rank }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="class_name" label="班级" />
            <el-table-column prop="avg_score" label="平均分" />
          </el-table>
          <div ref="classChartRef" style="height: 300px; margin-top: 20px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <h3>学生成绩排名</h3>
          <el-select v-model="filterClassId" placeholder="选择班级" clearable @change="loadStudentRankings" style="width: 180px; margin-bottom: 10px;">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-table :data="studentRankings" style="width: 100%" max-height="400">
            <el-table-column prop="rank" label="排名" width="80">
              <template #default="{ row }">
                <el-tag :type="getRankType(row.rank)">{{ row.rank }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="student_name" label="学生" />
            <el-table-column prop="class_name" label="班级" />
            <el-table-column prop="avg_score" label="平均分" />
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="chart-card">
          <h3>科目排名</h3>
          <el-select v-model="selectedSubject" placeholder="选择科目" @change="loadSubjectRankings" style="width: 180px; margin-right: 10px;">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <el-table :data="subjectRankings" style="width: 100%" max-height="300">
            <el-table-column prop="rank" label="排名" width="80">
              <template #default="{ row }">
                <el-tag :type="getRankType(row.rank)">{{ row.rank }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="student_name" label="学生" />
            <el-table-column prop="score" label="成绩" />
            <el-table-column prop="exam_type" label="考试类型" />
            <el-table-column prop="semester" label="学期" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const semester = ref('')
const examType = ref('')
const filterClassId = ref(null)
const selectedSubject = ref(null)

const classes = ref([])
const subjects = ref([])
const classRankings = ref([])
const studentRankings = ref([])
const subjectRankings = ref([])

const classChartRef = ref(null)
let classChart = null

const getRankType = (rank) => {
  if (rank === 1) return 'danger'
  if (rank === 2) return 'warning'
  if (rank === 3) return 'success'
  return 'info'
}

const loadClasses = async () => {
  const data = await api.classes.list()
  classes.value = data || []
}

const loadSubjects = async () => {
  const data = await api.subjects.list()
  subjects.value = data || []
  if (subjects.value.length > 0) {
    selectedSubject.value = subjects.value[0].id
    loadSubjectRankings()
  }
}

const loadData = async () => {
  const data = await api.dashboard.getClassRankings({
    semester: semester.value,
    exam_type: examType.value
  })
  classRankings.value = (data || []).filter(r => r.class_id)
  updateClassChart()
}

const loadStudentRankings = async () => {
  const data = await api.dashboard.getStudentRankings({
    class_id: filterClassId.value,
    semester: semester.value,
    exam_type: examType.value,
    limit: 50
  })
  studentRankings.value = (data || []).filter(r => r.student_id)
}

const loadSubjectRankings = async () => {
  if (!selectedSubject.value) return
  const data = await api.dashboard.getSubjectRankings(selectedSubject.value, {
    semester: semester.value,
    exam_type: examType.value,
    limit: 20
  })
  subjectRankings.value = data || []
}

const updateClassChart = () => {
  if (!classChart || classRankings.value.length === 0) return
  
  const xData = classRankings.value.map(r => r.class_name)
  const yData = classRankings.value.map(r => r.avg_score)
  
  classChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xData },
    yAxis: { type: 'value', min: 0, max: 100 },
    series: [{
      data: yData.map((v, i) => ({
        value: v,
        itemStyle: { color: i < 3 ? '#f56c6c' : '#409eff' }
      })),
      type: 'bar',
      barWidth: '50%'
    }]
  })
}

watch([semester, examType], () => {
  loadData()
  loadStudentRankings()
  loadSubjectRankings()
})

onMounted(async () => {
  await Promise.all([loadClasses(), loadSubjects()])
  await loadData()
  await loadStudentRankings()
  
  classChart = echarts.init(classChartRef.value)
  updateClassChart()
  
  window.addEventListener('resize', () => classChart?.resize())
})
</script>

<style scoped>
.rankings {
  padding: 20px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}
</style>
