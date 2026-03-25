<template>
  <div class="points-container">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="学生总数" :value="stats.total_students">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="活跃学生" :value="stats.active_students">
            <template #prefix><el-icon><UserFilled /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="发放积分" :value="stats.total_points_distributed">
            <template #prefix><el-icon><Coin /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="兑换积分" :value="stats.total_points_exchanged">
            <template #prefix><el-icon><ShoppingCart /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab" class="points-tabs">
      <el-tab-pane label="积分排行" name="ranking">
        <el-card>
          <el-table :data="ranking" v-loading="loading" stripe>
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column label="学生" prop="student_name" />
            <el-table-column label="班级" prop="class_name" />
            <el-table-column label="积分" prop="total_points">
              <template #default="{ row }">
                <el-tag type="warning" size="large">{{ row.total_points }} 分</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="积分规则" name="rules">
        <el-card>
          <el-table :data="rules" v-loading="loading" stripe>
            <el-table-column label="类别" prop="category" width="120">
              <template #default="{ row }">
                <el-tag>{{ getCategoryText(row.category) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="规则名称" prop="name" />
            <el-table-column label="描述" prop="description" />
            <el-table-column label="积分" width="100">
              <template #default="{ row }">
                <el-tag type="success">+{{ row.points }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column v-if="isTeacher" label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="showAddPoints(row)">
                  发放积分
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="积分商城" name="shop">
        <el-row :gutter="20">
          <el-col :span="8" v-for="item in items" :key="item.id">
            <el-card class="item-card" shadow="hover">
              <div class="item-icon">
                <el-icon :size="48" :color="item.item_type === 'virtual' ? '#409EFF' : '#67C23A'">
                  <component :is="item.item_type === 'virtual' ? 'Star' : 'Box'" />
                </el-icon>
              </div>
              <h3>{{ item.name }}</h3>
              <p class="item-desc">{{ item.description }}</p>
              <div class="item-price">
                <el-tag type="warning" size="large">{{ item.points_cost }} 积分</el-tag>
              </div>
              <div class="item-stock">
                <span v-if="item.stock === -1">库存：无限</span>
                <span v-else>库存：{{ item.stock }}</span>
              </div>
              <el-button type="primary" class="exchange-btn" @click="exchangeItem(item)">
                立即兑换
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="兑换记录" name="exchanges">
        <el-card>
          <el-table :data="exchanges" v-loading="loading" stripe>
            <el-table-column label="商品" prop="item_name" />
            <el-table-column label="学生" prop="student_name" />
            <el-table-column label="消耗积分" prop="points_spent" />
            <el-table-column label="状态" prop="status">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="兑换时间">
              <template #default="{ row }">
                {{ formatDate(row.exchange_time) }}
              </template>
            </el-table-column>
            <el-table-column v-if="isTeacher" label="操作" width="150">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" size="small" type="success"
                  @click="completeExchange(row)">
                  确认领取
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="addPointsDialog" title="发放积分" width="500px">
      <el-form :model="addPointsForm" label-width="100px">
        <el-form-item label="选择学生">
          <el-select v-model="addPointsForm.student_id" placeholder="请选择学生" filterable>
            <el-option v-for="student in students" :key="student.id" :label="`${student.name} - ${student.class_name}`"
              :value="student.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="积分规则">
          <el-select v-model="addPointsForm.rule_id" placeholder="请选择规则">
            <el-option v-for="rule in rules" :key="rule.id" :label="`${rule.name} (+${rule.points})`"
              :value="rule.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="积分数量">
          <el-input-number v-model="addPointsForm.points" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="addPointsForm.description" placeholder="积分说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addPointsDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAddPoints">确认发放</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="exchangeDialog" title="帮学生兑换" width="500px">
      <div class="exchange-confirm">
        <el-form :model="exchangeForm" label-width="100px">
          <el-form-item label="选择学生" v-if="isTeacher">
            <el-select v-model="exchangeForm.student_id" placeholder="请选择学生" filterable>
              <el-option v-for="student in students" :key="student.id" :label="`${student.name} - ${student.class_name}`"
                :value="student.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="兑换商品">
            <el-tag type="warning" size="large">{{ selectedItem?.name }}</el-tag>
          </el-form-item>
          <el-form-item label="消耗积分">
            <el-tag type="danger" size="large">{{ selectedItem?.points_cost }} 积分</el-tag>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="exchangeDialog = false">取消</el-button>
        <el-button type="primary" @click="submitExchange">确认兑换</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { User, UserFilled, Coin, ShoppingCart, Star, Box } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const userStore = useUserStore()
const isAdmin = computed(() => userStore.isAdmin)
const isClassTeacher = computed(() => userStore.isClassTeacher)
const isTeacher = computed(() => userStore.isAdmin || userStore.isClassTeacher || userStore.userInfo?.role === 'teacher')

const stats = ref({ total_students: 0, active_students: 0, total_points_distributed: 0, total_points_exchanged: 0 })
const ranking = ref([])
const rules = ref([])
const items = ref([])
const exchanges = ref([])
const students = ref([])
const activeTab = ref('ranking')
const loading = ref(false)

const addPointsDialog = ref(false)
const addPointsForm = ref({ student_id: null, rule_id: null, points: 10, description: '' })
const selectedItem = ref(null)
const exchangeDialog = ref(false)
const exchangeForm = ref({ student_id: null })

const getCategoryText = (cat) => {
  const map = { attendance: '考勤', score: '成绩', behavior: '行为', homework: '作业', competition: '竞赛' }
  return map[cat] || cat
}

const getStatusType = (status) => {
  const map = { pending: 'warning', completed: 'success', cancelled: 'info' }
  return map[status] || ''
}

const getStatusText = (status) => {
  const map = { pending: '待领取', completed: '已领取', cancelled: '已取消' }
  return map[status] || status
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const fetchStats = async () => {
  try {
    const res = await api.get('/points/stats')
    stats.value = res.data
  } catch (e) {
    console.error('获取统计失败', e)
  }
}

const fetchRanking = async () => {
  try {
    const res = await api.get('/points/ranking?limit=50')
    ranking.value = res.data
  } catch (e) {
    console.error('获取排行失败', e)
  }
}

const fetchRules = async () => {
  try {
    const res = await api.get('/points/rules')
    rules.value = res.data
  } catch (e) {
    console.error('获取规则失败', e)
  }
}

const fetchItems = async () => {
  try {
    const res = await api.get('/points/items')
    items.value = res.data
  } catch (e) {
    console.error('获取商品失败', e)
  }
}

const fetchExchanges = async () => {
  try {
    const res = await api.get('/points/exchanges')
    exchanges.value = res.data.data
  } catch (e) {
    console.error('获取兑换记录失败', e)
  }
}

const fetchStudents = async () => {
  try {
    const res = await api.get('/students?page_size=1000')
    students.value = res.data.data.map(s => ({ ...s, class_name: s.class_name || '' }))
  } catch (e) {
    console.error('获取学生列表失败', e)
  }
}

const showAddPoints = (rule) => {
  addPointsForm.value = { student_id: null, rule_id: rule.id, points: rule.points, description: rule.name }
  addPointsDialog.value = true
}

const submitAddPoints = async () => {
  if (!addPointsForm.value.student_id) {
    ElMessage.warning('请选择学生')
    return
  }
  try {
    await api.post(`/points/students/${addPointsForm.value.student_id}/add`, addPointsForm.value)
    ElMessage.success('积分发放成功')
    addPointsDialog.value = false
    fetchStats()
    fetchRanking()
  } catch (e) {
    ElMessage.error('发放失败：' + (e.response?.data?.detail || '未知错误'))
  }
}

const exchangeItem = (item) => {
  selectedItem.value = item
  exchangeForm.value = { student_id: null }
  exchangeDialog.value = true
}

const submitExchange = async () => {
  if (isTeacher.value && !exchangeForm.value.student_id) {
    ElMessage.warning('请选择学生')
    return
  }
  try {
    const payload = { item_id: selectedItem.value.id }
    if (isTeacher.value) {
      payload.student_id = exchangeForm.value.student_id
    }
    await api.post('/points/exchange', payload)
    ElMessage.success('兑换成功！')
    exchangeDialog.value = false
    fetchExchanges()
    fetchStats()
  } catch (e) {
    ElMessage.error('兑换失败：' + (e.response?.data?.detail || '未知错误'))
  }
}

const completeExchange = async (exchange) => {
  try {
    await api.put(`/points/exchanges/${exchange.id}/complete`)
    ElMessage.success('兑换已完成')
    fetchExchanges()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchStats()
  fetchRanking()
  fetchRules()
  fetchItems()
  fetchExchanges()
  fetchStudents()
})
</script>

<style scoped>
.points-container { padding: 20px; }
.stats-row { margin-bottom: 20px; }
.points-tabs { margin-top: 20px; }
.item-card { text-align: center; margin-bottom: 20px; }
.item-icon { margin-bottom: 10px; }
.item-desc { color: #666; margin: 10px 0; min-height: 40px; }
.item-price { margin: 15px 0; }
.item-stock { color: #999; margin-bottom: 15px; }
.exchange-btn { width: 100%; }
.exchange-confirm { text-align: center; padding: 20px; }
</style>
