<template>
  <el-container class="admin-layout">
    <el-aside width="200px">
      <div class="logo">
        <img src="@/assets/身份识别认证.png" alt="Logo" class="logo-img" />
        <span>管理员系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>控制台</span>
        </el-menu-item>
        <el-menu-item index="/admin/employee">
          <el-icon><User /></el-icon>
          <span>员工管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/surgery">
          <el-icon><Bell /></el-icon>
          <span>手术通知</span>
        </el-menu-item>
        <el-menu-item index="/admin/attendance">
          <el-icon><Calendar /></el-icon>
          <span>考勤记录</span>
        </el-menu-item>
        <el-menu-item index="/admin/leave">
          <el-icon><Document /></el-icon>
          <span>请假审批</span>
        </el-menu-item>
        <el-menu-item index="/admin/face">
          <el-icon><Camera /></el-icon>
          <span>人脸采集</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>管理员系统</h2>
          <el-dropdown>
            <span class="el-dropdown-link">
              管理员
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { DataLine, User, Bell, Calendar, Document, Camera, ArrowDown } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      localStorage.removeItem('userInfo')
      ElMessage.success('已退出登录')
      router.push('/')
    })
    .catch(() => {})
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #2b2f3a;
  color: #fff;
}

.logo-img {
  width: 32px;
  height: 32px;
  margin-right: 10px;
  object-fit: contain;
}

.logo span {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
}

.el-aside {
  background-color: #304156;
}

.el-menu-vertical {
  height: 100%;
  border-right: none;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style> 