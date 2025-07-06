<template>
  <div class="leave-approval">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>请假审批</span>
        </div>
      </template>

      <div class="search-bar">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
        <el-input
          v-model="searchQuery"
          placeholder="搜索员工姓名"
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="departmentFilter" placeholder="选择部门" clearable>
          <el-option
            v-for="item in departments"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select v-model="statusFilter" placeholder="审批状态" clearable>
          <el-option label="待审批" value="待审批" />
          <el-option label="已通过" value="已通过" />
          <el-option label="已拒绝" value="已拒绝" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div v-if="isLoading" class="loading-container" v-loading="isLoading" element-loading-text="正在加载数据...">
      </div>
      <div v-else-if="!filteredApplications.length" class="no-data-container">
        <p>暂无数据</p>
      </div>
      <el-table v-else :data="filteredApplications" style="width: 100%">
        <el-table-column prop="employee_id" label="序号" width="100" />
        <el-table-column prop="employee_name" label="姓名" width="120" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="leave_type" label="请假类型" width="120" />
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="leave_days" label="请假天数" width="100" />
        <el-table-column prop="leave_reason" label="请假原因" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button-group v-if="scope.row.status === '待审批'">
              <el-button type="success" size="small" @click="handleApprove(scope.row)">
                批准
              </el-button>
              <el-button type="danger" size="small" @click="handleReject(scope.row)">
                拒绝
              </el-button>
            </el-button-group>
            <span v-else>已处理</span>
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
    <el-dialog
      v-model="approvalDialogVisible"
      :title="approvalType === 'approve'? '批准请假' : '拒绝请假'"
      width="500px"
    >
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="approvalDialogVisible = false">取消</el-button>
          <el-button
            :type="approvalType === 'approve'? 'success' : 'danger'"
            @click="handleApprovalSubmit"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import axios from 'axios'

const dateRange = ref([])
const searchQuery = ref('')
const departmentFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const approvalDialogVisible = ref(false)
const approvalType = ref('approve')
const currentApplication = ref(null)
const isLoading = ref(false) 

const departments = [
  { value: '外科', label: '外科' },
  { value: '内科', label: '内科' },
  { value: '急诊科', label: '急诊科' },
  { value: '儿科', label: '儿科' }
];

const leaveApplications = ref([])
const filteredApplications = computed(() => {
  return leaveApplications.value.filter((application) => {
    const startDate = new Date(application.start_date);
    const endDate = new Date(application.end_date);
    const searchQueryLower = searchQuery.value.toLowerCase();
    const employeeName = application.employee_name || '';
    const employeeNameLower = employeeName.toLowerCase();
    const employeeId = application.employee_id || 0; 
    const employeeIdStr = employeeId.toString();
    const matchesDate = !dateRange.value.length || (
      startDate >= new Date(dateRange.value[0]) &&
      endDate <= new Date(dateRange.value[1])
    );
    const matchesSearch = !searchQuery.value || (
      employeeNameLower.includes(searchQueryLower) ||
      employeeIdStr.includes(searchQuery.value)
    );
    const matchesDepartment = !departmentFilter.value || application.department === departmentFilter.value;
    const matchesStatus = !statusFilter.value || application.status === statusFilter.value;
    return matchesDate && matchesSearch && matchesDepartment && matchesStatus;
  });
});

const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return statusMap[status] || 'info'
}

const getLeaveApplications = async () => {
  isLoading.value = true; 
  try {
    const response = await axios.get(`/api/admin/leave-applications`, {
      params: {
        page: currentPage.value,
        size: pageSize.value,
        search: searchQuery.value,
        department: departmentFilter.value,
        status: statusFilter.value,
        startDate: dateRange.value[0],
        endDate: dateRange.value[1]
      }
    })
    if (response.status === 200) {
      leaveApplications.value = response.data.map(item => ({
        employee_id: item.id || '未知工号',
        employee_name: item.name || '未知姓名', 
        department: item.department || '未知部门',
        leave_type: item.leaveType || '未知类型', 
        start_date: item.startDate || '未知日期',
        end_date: item.endDate || '未知日期',
        leave_days: item.days || 0,
        leave_reason: item.reason || '未填写原因', 
        status: item.status || 'pending'
      }))
      total.value = parseInt(response.headers['total-count'] || 0)
    } else {
      ElMessage.error('获取请假申请列表失败，请检查网络或稍后重试')
    }
  } catch (error) {
    console.error('获取请假申请列表失败', error)
    ElMessage.error('获取请假申请列表失败，请检查网络或稍后重试')
  } finally {
    isLoading.value = false;
  }
}

const handleSearch = async () => {
  isLoading.value = true; 
  try {
    const response = await axios.get(`/api/admin/leave-applications`, {
      params: {
        page: currentPage.value,
        size: pageSize.value,
        search: searchQuery.value,
        department: departmentFilter.value,
        status: statusFilter.value,
        startDate: dateRange.value[0],
        endDate: dateRange.value[1]
      }
    })
    if (response.status === 200) {
      leaveApplications.value = response.data.map(item => ({
        employee_id: item.id || '未知工号',
        employee_name: item.name || '未知姓名', 
        department: item.department || '未知部门',
        leave_type: item.leaveType || '未知类型', 
        start_date: item.startDate || '未知日期',
        end_date: item.endDate || '未知日期',
        leave_days: item.days || 0,
        leave_reason: item.reason || '未填写原因', 
        status: item.status || 'pending'
      }))
      total.value = parseInt(response.headers['total-count'] || 0)
      ElMessage.success('查询成功')
    } else {
      ElMessage.error('搜索请假申请失败，请检查网络或稍后重试')
    }
  } catch (error) {
    console.error('搜索请假申请失败', error)
    ElMessage.error('搜索请假申请失败，请检查网络或稍后重试')
  } finally {
    isLoading.value = false; 
  }
}

const handleApprove = (row) => {
  if (row && row.employee_id) { 
    approvalType.value = 'approve'
    currentApplication.value = row
    approvalDialogVisible.value = true
  } else {
    ElMessage.error('数据异常，无法批准')
  }
}

const handleReject = (row) => {
  if (row && row.employee_id) { 
    approvalType.value ='reject'
    currentApplication.value = row
    approvalDialogVisible.value = true
  } else {
    ElMessage.error('数据异常，无法拒绝')
  }
}

const approveLeave = async (applicationId) => {
  if (applicationId) { 
    try {
      const response = await axios.post(`/api/admin/leave-applications/${applicationId}/approve`)
      if (response.status === 200) {
        ElMessage.success('批准成功')
        getLeaveApplications()
      } else {
        ElMessage.error('批准请假失败，请检查网络或稍后重试')
      }
    } catch (error) {
      console.error('批准请假失败', error)
      ElMessage.error('批准请假失败，请检查网络或稍后重试')
    }
  } else {
    ElMessage.error('申请ID未定义，无法批准')
  }
}

const rejectLeave = async (applicationId) => {
  if (applicationId) { 
    try {
      const response = await axios.post(`/api/admin/leave-applications/${applicationId}/reject`)
      if (response.status === 200) {
        ElMessage.success('拒绝成功')
        getLeaveApplications()
      } else {
        ElMessage.error('拒绝请假失败，请检查网络或稍后重试')
      }
    } catch (error) {
      console.error('拒绝请假失败', error)
      ElMessage.error('拒绝请假失败，请检查网络或稍后重试')
    }
  } else {
    ElMessage.error('申请ID未定义，无法拒绝')
  }
}

const handleApprovalSubmit = async () => {
  const applicationId = currentApplication.value?.employee_id; 
  if (applicationId) {
    if (approvalType.value === 'approve') {
      await approveLeave(applicationId)
    } else {
      await rejectLeave(applicationId)
    }
    approvalDialogVisible.value = false
  } else {
    ElMessage.error('数据异常，无法提交审批')
  }
}

onMounted(() => {
  getLeaveApplications()
})
</script>

<style scoped>
.leave-approval {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  width: 200px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.no-data-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
</style>