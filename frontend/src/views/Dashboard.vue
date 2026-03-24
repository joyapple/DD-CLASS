<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">数据仪表盘</h1>
      <el-select v-model="semester" placeholder="选择学期" @change="loadStats" style="width: 200px">
        <el-option label="全部" value="" />
        <el-option label="2024-1" value="2024-1" />
        <el-option label="2024-2" value="2024-2" />
      </el-select>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon :size="30"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_students }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon :size="30"><School /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_classes }}</div>
            <div class="stat-label">班级数量</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon :size="30"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_scores }}</div>
            <div class="stat-label">成绩记录</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon :size="30"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.attendance_rate }}%</div>
            <div class="stat-label">考勤率</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <div class="chart-card">
          <h3>平均成绩: {{ stats.avg_score }}分</h3>
          <div ref="scoreChartRef" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <h3>最近成绩记录</h3>
          <el-table :data="stats.recent_scores" style="width: 100%" max-height="300">
            <el-table-column prop="student_name" label="学生" />
            <el-table-column prop="subject_name" label="科目" />
            <el-table-column prop="score" label="成绩" width="80" />
            <el-table-column prop="exam_type" label="考试类型" width="100" />
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <div class="chart-card">
          <h3>班级平均成绩排名</h3>
          <div ref="rankingChartRef" style="height: 300px;"></div>
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
const stats = reactive({
  total_students: 0,
  total_classes: 0,
  total_scores: 0,
  avg_score: 0,
  attendance_rate: 0,
  recent_scores: [],
  class_rankings: []
})

const scoreChartRef = ref(null)
const rankingChartRef = ref(null)
let scoreChart = null
let rankingChart = null

const loadStats = async () => {
  const data = await api.dashboard.getStats({ semester: semester.value })
  Object.assign(stats, data)
  updateCharts()
}

const loadRankings = async () => {
  const data = await api.dashboard.getClassRankings({ semester: semester.value })
  stats.class_rankings = (data || []).filter(r => r.class_id)
  updateRankingChart()
}

const updateCharts = () => {
  if (scoreChart) {
    scoreChart.setOption({
      series: [{
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        splitNumber: 8,
        axisLine: {
          lineStyle: {
            width: 6,
            color: [
              [0.3, '#67e0e3'],
              [0.7, '#37a2da'],
              [1, '#fd666d']
            ]
          }
        },
        pointer: {
          itemStyle: { color: 'auto' }
        },
        axisTick: { show: false },
        splitLine: { length: 10, lineStyle: { width: 2, color: '#999' } },
        axisLabel: { color: '#999', fontSize: 12 },
        detail: {
          valueAnimation: true,
          formatter: '{value}分',
          color: 'auto',
          fontSize: 24
        },
        data: [{ value: stats.avg_score }]
      }]
    })
  }
}

const updateRankingChart = () => {
  if (rankingChart && stats.class_rankings.length > 0) {
    const xData = stats.class_rankings.map(r => r.class_name)
    const yData = stats.class_rankings.map(r => r.avg_score)
    
    rankingChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: xData },
      yAxis: { type: 'value', min: 0, max: 100 },
      series: [{
        data: yData,
        type: 'bar',
        itemStyle: { color: '#409eff' }
      }]
    })
  }
}

onMounted(async () => {
  await loadStats()
  await loadRankings()
  
  scoreChart = echarts.init(scoreChartRef.value)
  rankingChart = echarts.init(rankingChartRef.value)
  
  updateCharts()
  updateRankingChart()
  
  window.addEventListener('resize', () => {
    scoreChart?.resize()
    rankingChart?.resize()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-top: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
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
