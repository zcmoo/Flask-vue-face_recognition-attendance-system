<template>
  <div class="attendance">
    <el-card shadow="hover" class="clock-card">
      <div class="clock-container">
        <div class="current-time">{{ currentTime }}</div>
        <div class="today-date">{{ todayDate }}</div>
        <div class="clock-status">
          <el-tag :type="todayClockStatus.type" size="large">
            {{ todayClockStatus.text }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>考勤记录</span>
          <div class="header-right">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleDateChange"
            />
            <el-select
              v-model="statusFilter"
              placeholder="状态筛选"
              clearable
              @change="handleStatusChange"
            >
              <el-option
                v-for="item in statusOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="filteredAttendance" style="width: 100%">
        <el-table-column prop="attendance_date" label="日期" min-width="20%" />
        <el-table-column prop="attendance_time" label="上班时间" min-width="20%" />
        <el-table-column prop="departure_time" label="下班时间" min-width="20%" />
        <el-table-column prop="attendance_status" label="状态" min-width="20%">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.attendance_status)">
              {{ getStatusText(scope.row.attendance_status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue';

const router = useRouter()

const dateRange = ref([])
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statusOptions = [
  { label: '正常', value: 'on_time' },
  { label: '迟到', value: 'late' },
  { label: '缺勤', value: 'absent' },
  { label: '请假', value: 'leave' },
  { label: '早退', value: 'early_departure' }
]

const attendanceRecords = ref([])

const filteredAttendance = computed(() => {
  let result = [...attendanceRecords.value]
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    result = result.filter(item => {
      const date = new Date(item.attendance_date)
      return date >= start && date <= end
    })
  }
  if (statusFilter.value) {
    result = result.filter(item => item.attendance_status === statusFilter.value)
  }
  
  return result
})

const getStatusType = (status) => {
  const statusMap = {
    'on_time':'success',
    'late': 'warning',
    'absent': 'danger',
    'leave': 'info',
    'early_departure': 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusTextMap = {
    'on_time': '正常',
    'late': '迟到',
    'leave': '请假',
    'absent': '缺勤',
    'early_departure': '早退'
  }
  return statusTextMap[status] || '未知'
}

const handleDateChange = () => {
  currentPage.value = 1
  fetchAttendanceRecords()
}

const handleStatusChange = () => {
  currentPage.value = 1
  fetchAttendanceRecords()
}

const currentTime = ref('')
const todayDate = ref('')
const clockInTime = ref(null)
const clockOutTime = ref(null)
let timer = null

const formatTime = (date) => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const seconds = date.getSeconds().toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

const formatDate = (date) => {
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${year}年${month}月${day}日 ${weekDays[date.getDay()]}`
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = formatTime(now)
  todayDate.value = formatDate(now)
}

const todayClockStatus = computed(() => {
  const today = new Date()
  const todayDateStr = formatDate(today)
  const todayRecord = attendanceRecords.value.find(record => {
    const recordDate = new Date(record.attendance_date)
    return formatDate(recordDate) === todayDateStr
  })

  if (!todayRecord) {
    return { text: '未打卡', type: 'info' }
  }

  if (todayRecord.attendance_time && !todayRecord.departure_time) {
    return { text: '已上班打卡', type: 'success' }
  }

  if (todayRecord.attendance_time && todayRecord.departure_time) {
    return { text: '已下班打卡', type: 'success' }
  }

  return { text: '未打卡', type: 'info' }
})

const canClockIn = computed(() => {
  const today = new Date()
  const todayDateStr = formatDate(today)
  const hasTodayRecord = attendanceRecords.value.some(record => {
    const recordDate = new Date(record.attendance_date)
    return formatDate(recordDate) === todayDateStr
  })
  return!hasTodayRecord
})

const canClockOut = computed(() => {
  const today = new Date()
  const todayDateStr = formatDate(today)
  const hasTodayRecord = attendanceRecords.value.some(record => {
    const recordDate = new Date(record.attendance_date)
    return formatDate(recordDate) === todayDateStr
  })
  return hasTodayRecord &&!clockOutTime.value && clockInTime.value
})

const handleClockIn = () => {
  router.push('/staff/face-recognition')
}

const handleClockOut = () => {
  router.push('/staff/face-recognition')
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  fetchAttendanceRecords()
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

const fetchAttendanceRecords = async () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    const userInfo = JSON.parse(storedUserInfo)
    try {
      const response = await axios.get(`/api/employee/get_attendance_records/${userInfo.username}`, {
        params: {
          page: currentPage.value,
          pageSize: pageSize.value,
          start_date: dateRange.value.length === 2? dateRange.value[0].toISOString().split('T')[0] : null,
          end_date: dateRange.value.length === 2? dateRange.value[1].toISOString().split('T')[0] : null,
          status: statusFilter.value
        }
      })
      if (response.data.success) {
        attendanceRecords.value = response.data.data
        total.value = response.data.total
      } else {
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      ElMessage.error('获取考勤记录失败，请稍后重试')
    }
  }
}

watch(dateRange, (newValue) => {
  currentPage.value = 1
  fetchAttendanceRecords()
}, { immediate: false, deep: true })
</script>

<style scoped>
.attendance {
  padding: 20px;
}

.clock-card {
  margin-bottom: 20px;
}

.clock-container {
  text-align: center;
  padding: 20px;
}

.current-time {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
  font-family: 'Arial', sans-serif;
  margin-bottom: 10px;
}

.today-date {
  font-size: 18px;
  color: #606266;
  margin-bottom: 20px;
}

.clock-status {
  margin-bottom: 30px;
}

.clock-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.stat-card {
  height: 160px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.stat-content {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-right {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>