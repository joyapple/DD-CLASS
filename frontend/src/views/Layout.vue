<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>班级管理</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/classes" v-if="userStore.isAdmin">
          <el-icon><School /></el-icon>
          <span>班级管理</span>
        </el-menu-item>
        <el-menu-item index="/students">
          <el-icon><User /></el-icon>
          <span>学生管理</span>
        </el-menu-item>
        <el-menu-item index="/scores">
          <el-icon><Document /></el-icon>
          <span>成绩管理</span>
        </el-menu-item>
        <el-menu-item index="/attendance">
          <el-icon><Calendar /></el-icon>
          <span>考勤管理</span>
        </el-menu-item>
        <el-menu-item index="/rankings">
          <el-icon><TrendCharts /></el-icon>
          <span>班级排名</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><PieChart /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
        <el-menu-item index="/users" v-if="userStore.isAdmin">
          <el-icon><UserFilled /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/subjects" v-if="userStore.isAdmin">
          <el-icon><Reading /></el-icon>
          <span>科目管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="username">{{ userStore.userInfo?.real_name }}</span>
          <el-tag :type="userStore.isAdmin ? 'danger' : 'success'" size="small">
            {{ userStore.isAdmin ? '管理员' : '班主任' }}
          </el-tag>
        </div>
        <div class="header-right">
          <el-button type="danger" size="small" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { 
  DataAnalysis, School, User, Document, Calendar, 
  TrendCharts, PieChart, UserFilled, Reading, SwitchButton 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.sidebar {
  background-color: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
}

.logo h2 {
  color: white;
  font-size: 18px;
  margin: 0;
}

.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-weight: 500;
  color: #303133;
}

.main-content {
  background-color: #f5f7fa;
}
</style>
