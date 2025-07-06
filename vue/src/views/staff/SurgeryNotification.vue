<template>
  <div class="surgery-notification">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>手术通知</span>
          <div class="header-right">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="handleDateChange"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              :disabled-date="disabledDate"
            />
          </div>
        </div>
      </template>

      <el-table 
        :data="paginatedSurgeries" 
        style="width: 100%; text-align: center;"
        :header-cell-style="{ textAlign: 'center', padding: '10px' }"
        :cell-style="{ textAlign: 'center' }"
      >
        <el-table-column prop="surgery_date" label="日期" min-width="120" />
        <el-table-column prop="surgery_time" label="时间" min-width="120" />
        <el-table-column prop="patient_name" label="患者姓名" min-width="120" />
        <el-table-column prop="surgery_type" label="手术类型" min-width="120" />
        <el-table-column prop="operating_room" label="手术室" min-width="120" />
        <el-table-column prop="department" label="科室" min-width="120" />
        <el-table-column prop="notes" label="备注" min-width="120" />
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const surgeries = ref([])

const filteredSurgeries = computed(() => {
  let result = [...surgeries.value]
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    result = result.filter(item => {
      const date = new Date(item.surgery_date)
      return date >= new Date(start) && date <= new Date(end)
    })
  }
  return result
})

const paginatedSurgeries = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSurgeries.value.slice(start, end)
})

const disabledDate = (time) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return time < today
}

const handleDateChange = () => {
  currentPage.value = 1
  fetchSurgeries()
}

const fetchSurgeries = async () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    const userInfo = JSON.parse(storedUserInfo)
    try {
      const [startDate, endDate] = dateRange.value || [null, null]
      const response = await axios.get(`/api/employee/get_surgeries/${userInfo.username}`, {
        params: {
          page: currentPage.value,
          size: pageSize.value,
          start_date: startDate,
          end_date: endDate
        }
      })
      if (response.status === 200) {
        surgeries.value = response.data.data.map(surgery => ({
          surgery_date: surgery.date,
          surgery_time: surgery.time,
          patient_name: surgery.patient_name,
          surgery_type: surgery.surgery_type,
          operating_room: surgery.room,
          department: surgery.department,
          notes: surgery.remark
        }))
        total.value = response.data.total
      } else if (response.status === 404) {
        surgeries.value = []
        total.value = 0
      }
    } catch (error) {
      console.error('Error fetching surgeries:', error)
      if (error.response && error.response.data && error.response.data.message) {
      }
    }
  }
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
  fetchSurgeries()
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
  fetchSurgeries()
}

onMounted(() => {
  fetchSurgeries()
})
</script>

<style scoped>
.surgery-notification {
  padding: 20px;
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

:deep(.el-table .el-table__header th) {
  width: auto !important;
  flex: 1;
  text-align: center;
}

:deep(.el-table .el-table__body td) {
  text-align: center;
}
</style>