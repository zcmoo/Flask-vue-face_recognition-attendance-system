<template>
  <el-menu
    mode="horizontal"
    :router="true"
    class="navbar"
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>首页</span>
    </el-menu-item>
    
    <el-menu-item v-if="isStaff" index="/staff/face-recognition">
      <el-icon><Camera /></el-icon>
      <span>人脸识别</span>
    </el-menu-item>
    
    <el-menu-item v-if="isStaff" index="/staff/dashboard">
      <el-icon><User /></el-icon>
      <span>员工仪表盘</span>
    </el-menu-item>
    
    <el-menu-item v-if="isAdmin" index="/admin/dashboard">
      <el-icon><Setting /></el-icon>
      <span>管理员仪表盘</span>
    </el-menu-item>
    
    <div class="user-info">
      <span>{{ username }}</span>
      <el-button type="text" @click="handleLogout">退出登录</el-button>
    </div>
  </el-menu>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HomeFilled, Camera, User, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
const username = ref(userInfo.username || '')

const isStaff = computed(() => userInfo.userType === 'staff')
const isAdmin = computed(() => userInfo.userType === 'admin')

const handleLogout = () => {
  localStorage.removeItem('userInfo')
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.user-info {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-button {
  padding: 0;
}
</style> 