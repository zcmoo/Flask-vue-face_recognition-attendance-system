<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>今日考勤</span>
            </div>
          </template>
          <div class="stat-content">
            <div class="stat-value">{{ attendanceStatus }}</div>
            <div class="stat-label">状态</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>待处理手术</span>
            </div>
          </template>
          <div class="stat-content">
            <div class="stat-value">{{ pendingSurgeries }}</div>
            <div class="stat-label">台</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>请假申请</span>
            </div>
          </template>
          <div class="stat-content">
            <div class="stat-value">{{ leaveApplications }}</div>
            <div class="stat-label">个</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>本月出勤率</span>
            </div>
          </template>
          <div class="stat-content">
            <div class="stat-value">{{ attendanceRate }}%</div>
            <div class="stat-label">出勤率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-card class="surgery-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>今日手术安排</span>
          <el-button type="primary" link @click="viewAllSurgeries">
            查看全部
          </el-button>
        </div>
      </template>
      <el-table :data="todaySurgeries" style="width: 100%">
        <el-table-column prop="surgery_date" label="日期" min-width="120" />
        <el-table-column prop="surgery_time" label="时间" min-width="120" />
        <el-table-column prop="patient_name" label="患者姓名" min-width="120" />
        <el-table-column prop="surgery_type" label="手术类型" min-width="120" />
        <el-table-column prop="operating_room" label="手术室" min-width="120" />
        <el-table-column prop="department" label="科室" min-width="120" />
        <el-table-column prop="notes" label="备注" min-width="120" />
      </el-table>
    </el-card>
    <el-card class="attendance-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>最近考勤记录</span>
          <el-button type="primary" link @click="viewAllAttendance">
            查看全部
          </el-button>
        </div>
      </template>
      <el-table :data="filteredAttendance" style="width: 100%">
        <el-table-column prop="attendance_date" label="日期" min-width="20%" />
        <el-table-column prop="attendance_time" label="上班时间" min-width="20%" />
        <el-table-column prop="departure_time" label="下班时间" min-width="20%" />
        <el-table-column prop="attendance_status" label="状态" min-width="20%">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.attendance_status)">
              {{ scope.row.attendance_status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const attendanceStatus = ref('')
const pendingSurgeries = ref(0)
const leaveApplications = ref(0)
const attendanceRate = ref(0)
const todaySurgeries = ref([])
const attendanceRecords = ref([])
const filteredAttendance = computed(() => {
  return attendanceRecords.value
})
const getStatusType = (status) => {
  const statusMap = {
    '待开始': 'info',
    '准备中': 'warning',
    '进行中': 'primary',
    '已完成': 'success',
    '已取消': 'danger',
    '正常': 'success',
    '迟到': 'warning',
    '早退': 'warning',
    '缺勤': 'danger'
  }
  return statusMap[status] || 'info'
}

const viewAllSurgeries = () => {
  router.push('/staff/surgery')
}

const viewAllAttendance = () => {
  router.push('/staff/attendance')
}

onMounted(async () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    const userInfo = JSON.parse(storedUserInfo)
    try {
      const response = await axios.get(`/api/employee/get_dashboard_data/${userInfo.username}`)
      const data = response.data
      const attendanceStatusMap = {
        'on_time': '正常',
        'late': '迟到',
        'early_leave': '早退',
        'absent': '缺勤'
      };
      attendanceStatus.value = attendanceStatusMap[data.attendance_status] || data.attendance_status;
      pendingSurgeries.value = data.pendingSurgeries
      leaveApplications.value = data.leaveApplications
      attendanceRate.value = data.attendanceRate
      todaySurgeries.value = data.todaySurgeries.map(surgery => ({
        surgery_date: surgery.date,
        surgery_time: surgery.time,
        patient_name: surgery.patient_name,
        surgery_type: surgery.surgery_type,
        operating_room: surgery.room,
        department: surgery.department,
        notes: surgery.remark
      }))
      attendanceRecords.value = data.recentAttendance.map(record => ({
        attendance_date: record.date,
        attendance_time: record.attendance_time,
        departure_time: record.departure_time,
        attendance_status: attendanceStatusMap[record.status] || record.status
      }))
    } catch (error) {
      console.error('获取数据失败:', error)
    }
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-content {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.surgery-card,
.attendance-card {
  margin-top: 20px;
}
</style>