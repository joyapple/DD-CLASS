import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const message = error.response.data?.detail || '请求失败'
      ElMessage.error(message)
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default {
  auth: {
    login: (data) => api.post('/auth/login', data),
    register: (data) => api.post('/auth/register', data),
    getCurrentUser: () => api.get('/auth/me')
  },
  users: {
    list: (params) => api.get('/users', { params }),
    get: (id) => api.get(`/users/${id}`),
    create: (data) => api.post('/users', data),
    update: (id, data) => api.put(`/users/${id}`, data),
    delete: (id) => api.delete(`/users/${id}`)
  },
  classes: {
    list: () => api.get('/classes'),
    get: (id) => api.get(`/classes/${id}`),
    create: (data) => api.post('/classes', data),
    update: (id, data) => api.put(`/classes/${id}`, data),
    delete: (id) => api.delete(`/classes/${id}`)
  },
  students: {
    list: (params) => api.get('/students', { params }),
    get: (id) => api.get(`/students/${id}`),
    create: (data) => api.post('/students', data),
    update: (id, data) => api.put(`/students/${id}`, data),
    delete: (id) => api.delete(`/students/${id}`),
    batchCreate: (data) => {
      return api.post('/students/batch', JSON.stringify(data), {
        headers: { 'Content-Type': 'application/json' }
      })
    }
  },
  subjects: {
    list: () => api.get('/subjects'),
    create: (data) => api.post('/subjects', data),
    delete: (id) => api.delete(`/subjects/${id}`)
  },
  scores: {
    list: (params) => api.get('/scores', { params }),
    get: (id) => api.get(`/scores/${id}`),
    create: (data) => api.post('/scores', data),
    update: (id, data) => api.put(`/scores/${id}`, data),
    delete: (id) => api.delete(`/scores/${id}`),
    getStudentScores: (studentId, params) => api.get(`/scores/student/${studentId}`, { params })
  },
  semesters: {
    list: () => api.get('/semesters'),
    create: (data) => api.post('/semesters', data),
    delete: (id) => api.delete(`/semesters/${id}`)
  },
  attendance: {
    list: (params) => api.get('/attendance', { params }),
    create: (data) => api.post('/attendance', data),
    update: (id, data) => api.put(`/attendance/${id}`, data),
    delete: (id) => api.delete(`/attendance/${id}`),
    getClassStats: (classId, params) => api.get(`/attendance/statistics/class/${classId}`, { params }),
    getStudentStats: (studentId, params) => api.get(`/attendance/statistics/student/${studentId}`, { params })
  },
  dashboard: {
    getStats: (params) => api.get('/dashboard/stats', { params }),
    getClassRankings: (params) => api.get('/dashboard/rankings/classes', { params }),
    getStudentRankings: (params) => api.get('/dashboard/rankings/students', { params }),
    getSubjectRankings: (subjectId, params) => api.get(`/dashboard/rankings/subjects/${subjectId}`, { params }),
    getTrends: (params) => api.get('/dashboard/analysis/trends', { params }),
    getSubjectAnalysis: (params) => api.get('/dashboard/analysis/subjects', { params })
  },
  analytics: {
    getStudentAnalysis: (studentId, params) => api.get(`/analytics/student/${studentId}`, { params }),
    getClassAnalysis: (classId, params) => api.get(`/analytics/class/${classId}`, { params }),
    getComparison: (classId, params) => api.get('/analytics/comparison', { params })
  }
}
