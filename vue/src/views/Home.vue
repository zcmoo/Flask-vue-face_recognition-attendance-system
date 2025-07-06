<template>
  <div class="home-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Lock /></el-icon>
          <h2>医院人脸考勤系统</h2>
        </div>
      </template>
      <div class="login-form">
        <div class="form-item">
          <el-input
            v-model="workId"
            placeholder="工号"
            :prefix-icon="User"
          />
        </div>
        <div class="form-item">
          <el-input
            v-model="password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
          />
        </div>
        <div class="form-item">
          <el-select v-model="userType" placeholder="用户类型" class="user-type-select">
            <el-option label="员工登录" value="staff" />
            <el-option label="管理员登录" value="admin" />
          </el-select>
        </div>
        <div class="login-options">
          <div class="button-group">
            <el-button type="primary" size="large" @click="handleLogin">登录</el-button>
            <el-button type="info" size="large" @click="goToAttendance">直接考勤</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Lock, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const workId = ref('')
const password = ref('')
const userType = ref('')

const handleLogin = async () => {
  if (!workId.value || !password.value || !userType.value) {
    ElMessage.warning('请填写完整的登录信息')
    return
  }

  try {
    const formData = new FormData()
    formData.append('username', workId.value)
    formData.append('password', password.value)
    formData.append('user_type', userType.value === 'admin' ? 'admin' : 'employee')
    const response = await axios.post('/api/login/login', formData)
    if (response.data.message === '登录成功') {
      ElMessage.success('登录成功')
      const userInfo = {
        userType: userType.value,
        username: workId.value,
        name: response.data.user_name,
        department: response.data.user_department,
      }
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
      if (userType.value === 'admin') {
        router.push('/admin/dashboard')
      } else {
        router.push('/staff/dashboard')
      }
    } 
  } catch (error) {
    ElMessage.error('登录失败，请检查工号或密码')
    console.error('Login error:', error)
  }
}

const goToAttendance = () => {
  router.push('/staff/face-recognition')
}
</script>

<style scoped>
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-image: url('@/assets/首页.jpg');
  background-size: cover;
  background-position: center;
  position: relative;
}

.home-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.login-card {
  width: 400px;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9) !important;
  border: none;
  border-radius: 15px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.card-header {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px 0;
}

.header-icon {
  font-size: 24px;
  color: var(--el-color-primary);
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.login-form {
  padding: 20px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.user-type-select {
  width: 100%;
}

.login-options {
  margin-top: 30px;
}

.button-group {
  display: flex;
  gap: 15px;
  justify-content: space-between;
}

.el-button {
  flex: 1;
  height: 40px;
  font-size: 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.el-button:first-child {
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

.el-button:last-child {
  background: #909399;
  border-color: #909399;
}

.el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.el-button:first-child:hover {
  opacity: 0.9;
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

.el-button:last-child:hover {
  opacity: 0.9;
  background: #909399;
  border-color: #909399;
}

:deep(.el-input__wrapper) {
  border-radius: 20px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 20px;
}
</style>