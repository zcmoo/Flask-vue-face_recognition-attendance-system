<template>
  <div class="leave">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>请假申请</span>
          <el-button type="primary" @click="handleApply">申请请假</el-button>
        </div>
      </template>

      <el-table :data="leaveRecords" style="width: 100%">
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="leave_type" label="请假类型" width="120" />
        <el-table-column prop="leave_days" label="请假天数" width="100" />
        <el-table-column prop="leave_reason" label="请假原因" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === '待审批'"
              type="danger"
              link
              @click="handleCancel(scope.row)"
            >
              取消
            </el-button>
            <el-button
              v-if="scope.row.status !== '已拒绝' && scope.row.status !== '已取消'"
              type="primary"
              link
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
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
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑请假申请' : '申请请假'"
      width="50%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="请假类型" prop="leave_type">
          <el-select v-model="form.leave_type" placeholder="请选择请假类型">
            <el-option
              v-for="item in leaveTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="请假时间" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :disabled-date="disabledDate"
          />
        </el-form-item>

        <el-form-item label="请假原因" prop="leave_reason">
          <el-input
            v-model="form.leave_reason"
            type="textarea"
            :rows="3"
            placeholder="请输入请假原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const dialogVisible = ref(false)
const isEdit = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const formRef = ref(null)

const leaveTypes = [
  { label: '事假', value: '事假' },
  { label: '病假', value: '病假' },
  { label: '年假', value: '年假' },
  { label: '产假', value: '产假' },
  { label: '其他', value: '其他' }
]

const form = ref({
  leave_type: '',
  dateRange: [],
  leave_reason: ''
})

const rules = {
  leave_type: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择请假时间', trigger: 'change' }],
  leave_reason: [{ required: true, message: '请输入请假原因', trigger: 'blur' }]
}

const leaveRecords = ref([])

const getStatusType = (status) => {
  const statusMap = {
    '待审批': 'warning',
    '已批准': 'success',
    '已拒绝': 'danger',
    '已取消': 'info'
  }
  return statusMap[status] || 'info'
}

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 
}

const handleApply = () => {
  isEdit.value = false
  form.value = {
    leave_type: '',
    dateRange: [],
    leave_reason: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogVisible.value = true
  form.value = {
    ...row,
    dateRange: [new Date(row.start_date), new Date(row.end_date)]
  }
}

const handleCancel = async (row) => {
  ElMessageBox.confirm('确定要取消该请假申请吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  .then(async () => {
      const storedUserInfo = localStorage.getItem('userInfo')
      if (storedUserInfo) {
        const userInfo = JSON.parse(storedUserInfo)
        try {
          const response = await axios.post(`/api/employee/cancel_leave/${userInfo.username}/${row.id}`)
          if (response.data.success) {
            ElMessage.success('取消成功')
            fetchLeaveRecords()
          } else {
            ElMessage.error(response.data.message)
          }
        } catch (error) {
          ElMessage.error('取消失败，请稍后重试')
        }
      }
    })
  .catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      const storedUserInfo = localStorage.getItem('userInfo')
      if (storedUserInfo) {
        const userInfo = JSON.parse(storedUserInfo)
        const [startDate, endDate] = form.value.dateRange
        const data = {
          start_date: startDate.toISOString().split('T')[0],
          end_date: endDate.toISOString().split('T')[0],
          leave_type: form.value.leave_type,
          leave_reason: form.value.leave_reason,
          employee_id: userInfo.username,
          employee_name: userInfo.name,
          department: userInfo.department
        }
        try {
          let url
          if (isEdit.value) {
            url = `/api/employee/edit_leave/${userInfo.username}/${form.value.id}`
          } else {
            url = `/api/employee/apply_leave/${userInfo.username}`
          }
          const response = await axios.post(url, data)
          if (response.data.success) {
            ElMessage.success(isEdit.value ? '修改成功' : '提交成功')
            dialogVisible.value = false
            fetchLeaveRecords()
          } else {
            ElMessage.error(response.data.message)
          }
        } catch (error) {
          ElMessage.error(isEdit.value ? '修改失败，请稍后重试' : '提交失败，请稍后重试')
        }
      }
    }
  })
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  fetchLeaveRecords()
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
  fetchLeaveRecords()
}

const fetchLeaveRecords = async () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    const userInfo = JSON.parse(storedUserInfo)
    try {
      const response = await axios.get(`/api/employee/get_leave_records/${userInfo.username}`, {
        params: {
          page: currentPage.value,
          pageSize: pageSize.value
        }
      })
      if (response.data.success) {
        leaveRecords.value = response.data.data
        total.value = response.data.total
      } else {
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      ElMessage.error('获取请假记录失败，请稍后重试')
    }
  }
}

onMounted(() => {
  fetchLeaveRecords()
})
</script>

<style scoped>
.leave {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

:deep(.el-table .el-table__header th) {
  flex: 1 !important;
  text-align: center;
}

:deep(.el-table .el-table__body td) {
  flex: 1 !important;
  text-align: center;
}
</style>