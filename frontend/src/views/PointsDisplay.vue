<template>
  <div class="display-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🏆 积分龙虎榜</h1>
          <el-tag type="warning" size="large" effect="dark">实时排名</el-tag>
        </div>
      </el-header>

      <el-main>
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="ranking-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Trophy /></el-icon> 积分排行榜</span>
                  <el-button type="primary" :icon="FullScreen" circle @click="toggleFullscreen" />
                </div>
              </template>

              <el-table :data="ranking" stripe v-loading="loading" :show-header="true">
                <el-table-column label="排名" width="100" align="center">
                  <template #default="{ $index }">
                    <div class="rank-badge" :class="getRankClass($index)">
                      {{ $index + 1 }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="学生信息">
                  <template #default="{ row }">
                    <div class="student-info">
                      <el-avatar :size="40" :style="{ backgroundColor: getAvatarColor(row.student_name) }">
                        {{ row.student_name?.charAt(0) }}
                      </el-avatar>
                      <div class="info">
                        <div class="name">{{ row.student_name }}</div>
                        <div class="class">{{ row.class_name }}</div>
                      </div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="积分" width="150" align="center">
                  <template #default="{ row }">
                    <el-tag type="warning" size="large" effect="dark">
                      <el-icon><Coin /></el-icon> {{ row.total_points }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>

          <el-col :span="8">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-card class="stat-card" shadow="hover">
                  <el-statistic title="参与学生" :value="stats.total_students">
                    <template #prefix><el-icon :size="20"><User /></el-icon></template>
                  </el-statistic>
                </el-card>
              </el-col>
              <el-col :span="24">
                <el-card class="stat-card" shadow="hover">
                  <el-statistic title="积分发放" :value="stats.total_points_distributed">
                    <template #prefix><el-icon :size="20"><Plus /></el-icon></template>
                  </el-statistic>
                </el-card>
              </el-col>
              <el-col :span="24">
                <el-card class="stat-card" shadow="hover">
                  <el-statistic title="积分兑换" :value="stats.total_points_exchanged">
                    <template #prefix><el-icon :size="20"><ShoppingCart /></el-icon></template>
                  </el-statistic>
                </el-card>
              </el-col>
            </el-row>

            <el-card class="top3-card" shadow="hover">
              <template #header>
                <span><el-icon><Medal /></el-icon> TOP 3</span>
              </template>
              <div class="top3-list">
                <div v-for="(item, index) in topThree" :key="index" class="top3-item">
                  <el-badge :value="index + 1" :type="getBadgeType(index)" class="badge">
                    <el-avatar :size="50" :style="{ backgroundColor: getAvatarColor(item.student_name) }">
                      {{ item.student_name?.charAt(0) }}
                    </el-avatar>
                  </el-badge>
                  <div class="top3-info">
                    <div class="name">{{ item.student_name }}</div>
                    <div class="points">
                      <el-icon><Coin /></el-icon> {{ item.total_points }}
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>

      <el-footer>
        <div class="footer-content">
          <span>{{ currentTime }}</span>
          <el-button type="primary" plain @click="refresh">
            <el-icon><Refresh /></el-icon> 刷新数据
          </el-button>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Trophy, Coin, User, ShoppingCart, Medal, FullScreen,
  Refresh, Plus
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const ranking = ref([])
const stats = ref({ total_students: 0, active_students: 0, total_points_distributed: 0, total_points_exchanged: 0 })
const loading = ref(false)
const currentTime = ref('')
let timer = null

const topThree = computed(() => ranking.value.slice(0, 3))

const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']

const getAvatarColor = (name) => {
  if (!name) return '#409EFF'
  const index = name.charCodeAt(0) % colors.length
  return colors[index]
}

const getRankClass = (index) => {
  const classes = ['rank-gold', 'rank-silver', 'rank-bronze']
  return classes[index] || ''
}

const getBadgeType = (index) => {
  const types = ['gold', 'silver', 'bronze']
  return types[index] || ''
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const fetchData = async () => {
  loading.value = true
  try {
    const [statsRes, rankingRes] = await Promise.all([
      api.get('/points/stats'),
      api.get('/points/ranking?limit=20')
    ])
    stats.value = statsRes.data
    ranking.value = rankingRes.data
  } catch (e) {
    console.error('获取数据失败', e)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  fetchData()
  ElMessage.success('数据已刷新')
}

const toggleFullscreen = async () => {
  if (!document.fullscreenElement) {
    await document.documentElement.requestFullscreen()
  } else {
    await document.exitFullscreen()
  }
}

onMounted(() => {
  updateTime()
  fetchData()
  timer = setInterval(() => {
    updateTime()
    fetchData()
  }, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.display-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 28px;
}

.el-main {
  padding: 20px;
}

.ranking-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rank-badge {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  background: #909399;
  color: white;
  margin: 0 auto;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700, #ffb347);
  color: #333;
}

.rank-silver {
  background: linear-gradient(135deg, #c0c0c0, #a9a9a9);
  color: #333;
}

.rank-bronze {
  background: linear-gradient(135deg, #cd7f32, #b87333);
  color: white;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-info .info {
  display: flex;
  flex-direction: column;
}

.student-info .name {
  font-weight: bold;
  font-size: 16px;
}

.student-info .class {
  font-size: 12px;
  color: #909399;
}

.stat-card {
  margin-bottom: 20px;
  border-radius: 12px;
  text-align: center;
}

.top3-card {
  margin-top: 20px;
  border-radius: 12px;
}

.top3-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.top3-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.top3-info {
  flex: 1;
}

.top3-info .name {
  font-weight: bold;
  font-size: 16px;
}

.top3-info .points {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #e6a23c;
  font-weight: bold;
  margin-top: 5px;
}

.el-footer {
  background: #fff;
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
