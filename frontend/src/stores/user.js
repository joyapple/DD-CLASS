import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isTeacher = computed(() => userInfo.value?.role === 'teacher')
  const classId = computed(() => userInfo.value?.class_id)

  async function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const data = await api.auth.login(formData)
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    
    const userData = await api.auth.getCurrentUser()
    userInfo.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
    
    return userData
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    isTeacher,
    classId,
    login,
    logout
  }
})
