<template>
  <div class="attendance-records">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>考勤记录查询</span>
        </div>
      </template>

      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索员工姓名/工号"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="考勤状态" clearable>
          <el-option label="正常" value="on_time" />
          <el-option label="迟到" value="late" />
          <el-option label="早退" value="early_departure" />
          <el-option label="缺勤" value="absent" />
          <el-option label="请假" value="leave" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>

      <el-table :data="filteredRecords" style="width: 100%">
        <el-table-column prop="attendance_date" label="日期" width="200" />
        <el-table-column prop="employee_id" label="工号" width="200" />
        <el-table-column prop="employee_name" label="姓名" width="150" />
        <el-table-column prop="attendance_time" label="上班时间" width="200" />
        <el-table-column prop="departure_time" label="下班时间" width="200" />
        <el-table-column prop="attendance_status" label="考勤状态" width="150">
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
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

const searchQuery = ref('');
const statusFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const attendanceRecords = ref([]);

const getStatusType = (status) => {
  const statusMap = {
    'on_time': 'success',
    'late': 'warning',
    'leave': 'warning',
    'absent': 'danger',
    'early_departure': 'warning'
  };
  return statusMap[status] || 'info';
};

const getStatusText = (status) => {
  const statusTextMap = {
    'on_time': '正常',
    'late': '迟到',
    'leave': '请假',
    'absent': '缺勤',
    'early_departure': '早退'
  };
  return statusTextMap[status] || '未知';
};

const filteredRecords = computed(() => {
  return attendanceRecords.value.filter(record => {
    const matchesSearch = !searchQuery.value || (
      record.employee_name.includes(searchQuery.value) ||
      record.employee_id.includes(searchQuery.value)
    );
    const matchesStatus = !statusFilter.value || (
      record.attendance_status === statusFilter.value
    );
    return matchesSearch && matchesStatus;
  });
});

const handleSearch = async () => {
  try {
    const response = await axios.get('/api/admin/get_attendance_records_kq', {
      params: {
        search: searchQuery.value,
        status: statusFilter.value,
        page: currentPage.value,
        pageSize: pageSize.value
      }
    });
    attendanceRecords.value = response.data.items;
    total.value = response.data.total;
    ElMessage.success('查询成功');
  } catch (error) {
    console.error('查询失败:', error);
    ElMessage.error('查询失败，请检查网络或重试');
  }
};

const handlePageChange = (newPage) => {
  currentPage.value = newPage;
  handleSearch();
};

onMounted(() => {
  handleSearch();
});
</script>

<style scoped>
.attendance-records {
  padding: 20px;
}

.search-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>