<template>
  <div class="staff-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px">
        <div class="logo">
          <img src="@/assets/身份识别认证.png" alt="Logo" class="logo-img" />
          <span>员工系统</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          :router="true"
        >
          <el-menu-item index="/staff/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>工作台</span>
          </el-menu-item>
          <el-menu-item index="/staff/profile">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </el-menu-item>
          <el-menu-item index="/staff/surgery">
            <el-icon><Calendar /></el-icon>
            <span>手术通知</span>
          </el-menu-item>
          <el-menu-item index="/staff/attendance">
            <el-icon><Timer /></el-icon>
            <span>考勤记录</span>
          </el-menu-item>
          <el-menu-item index="/staff/leave">
            <el-icon><Document /></el-icon>
            <span>请假申请</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <el-header>
          <div class="header-left">
            <el-icon class="toggle-sidebar" @click="toggleSidebar">
              <Fold v-if="isCollapse" />
              <Expand v-else />
            </el-icon>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/staff/dashboard' }">
                首页
              </el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentRoute }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-info">
                {{ userInfo.name }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Monitor,
  User,
  Calendar,
  Timer,
  Document,
  Fold,
  Expand,
  ArrowDown
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)

const userInfo = ref({ name: '张三', department: '外科' })
onMounted(() => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    try {
      const parsedUserInfo = JSON.parse(storedUserInfo)
      userInfo.value = {
        name: parsedUserInfo.name,
        department: parsedUserInfo.department
      }
    } catch (error) {
      console.error('Failed to parse userInfo from localStorage:', error)
    }
  } else {
    console.warn('No userInfo found in localStorage, using default value')
  }
})

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => {
  const routeMap = {
    '/staff/dashboard': '工作台',
    '/staff/profile': '个人资料',
    '/staff/surgery': '手术通知',
    '/staff/attendance': '考勤记录',
    '/staff/leave': '请假申请'
  }
  return routeMap[route.path] || ''
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleLogout = () => {
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
.staff-layout {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #2b2f3a;
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
}

.el-menu {
  border-right: none;
}

.el-menu-vertical {
  background-color: #304156;
}

.el-menu-vertical .el-menu-item {
  color: #bfcbd9;
}

.el-menu-vertical .el-menu-item:hover {
  background-color: #263445;
}

.el-menu-vertical .el-menu-item.is-active {
  background-color: #263445;
  color: #409eff;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-sidebar {
  font-size: 20px;
  cursor: pointer;
  margin-right: 20px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-info .el-icon {
  margin-left: 5px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style> 