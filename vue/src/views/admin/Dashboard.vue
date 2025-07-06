<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>员工总数</span>
            </div>
          </template>
          <div class="card-content">
            <div class="number">{{ employeeTotal }}</div>
            <div class="description">当前在职员工</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>今日考勤</span>
            </div>
          </template>
          <div class="card-content">
            <div class="number">{{ todayAttendanceCount }}</div>
            <div class="description">已打卡人数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>待审批请假</span>
            </div>
          </template>
          <div class="card-content">
            <div class="number">{{ pendingLeaveApplicationsCount }}</div>
            <div class="description">待处理申请</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>手术通知</span>
            </div>
          </template>
          <div class="card-content">
            <div class="number">{{ todaySurgeryNotificationsCount }}</div>
            <div class="description">今日手术安排</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>考勤统计</span>
            </div>
          </template>
          <div class="chart-container" ref="attendanceChartRef"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>请假统计</span>
            </div>
          </template>
          <div class="chart-container" ref="leaveChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row class="mt-20">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近考勤记录</span>
            </div>
          </template>
          <el-table :data="filteredRecords" style="width: 100%">
            <el-table-column prop="attendance_date" label="日期" width="180" />
            <el-table-column prop="employee_id" label="工号" width="150" />
            <el-table-column prop="employee_name" label="姓名" width="120" />
            <el-table-column prop="attendance_time" label="上班时间" width="150" />
            <el-table-column prop="departure_time" label="下班时间" width="150" />
            <el-table-column prop="attendance_status" label="考勤状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.attendance_status)">
                  {{ getStatusText(scope.row.attendance_status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';

const employeeTotal = ref(0);
const todayAttendanceCount = ref(0);
const pendingLeaveApplicationsCount = ref(0);
const todaySurgeryNotificationsCount = ref(0);
const attendanceRecords = ref([]);

const filteredRecords = computed(() => {
  const today = new Date().toISOString().split('T')[0];
  return attendanceRecords.value.filter(record => record.attendance_date === today);
});

const attendanceChartRef = ref(null);
const leaveChartRef = ref(null);

const getStatusType = (status) => {
  const statusMap = {
    'on_time': 'success',
    'late': 'warning',
    'leave': 'danger',
    'absent': 'warning',
    'early_departure': 'danger'
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
  return statusTextMap[status] || '未知状态';
};

onMounted(async () => {
  try {
    const response = await axios.get('/api/admin/get_dashboard_data');
    employeeTotal.value = response.data.employeeTotal;
    todayAttendanceCount.value = response.data.todayAttendanceCount;
    pendingLeaveApplicationsCount.value = response.data.pendingLeaveApplicationsCount;
    todaySurgeryNotificationsCount.value = response.data.todaySurgeryNotificationsCount;
    attendanceRecords.value = response.data.attendanceRecords;
    const today = new Date().toISOString().split('T')[0];
    const response1 = await axios.get(`/api/admin/get_attendance_records_kq?date=${today}`);
    const attendanceRecords1 = response1.data.items;
    if (attendanceRecords1 && Array.isArray(attendanceRecords1)) {
      const attendanceStatusCount = {
        'on_time': 0,
        'late': 0,
        'leave': 0,
        'absent': 0,
        'early_departure': 0
      };
      attendanceRecords1.forEach(record => {
        if (record.attendance_status === 'on_time') {
          attendanceStatusCount.on_time++;
        } else if (record.attendance_status === 'late') {
          attendanceStatusCount.late++;
        } else if (record.attendance_status === 'leave') {
          attendanceStatusCount.leave++;
        } else if (record.attendance_status === 'absent') {
          attendanceStatusCount.absent++;
        } else if (record.attendance_status === 'early_departure') {
          attendanceStatusCount.early_departure++;
        }
      });
      if (attendanceChartRef.value) {
        const attendanceChart = echarts.init(attendanceChartRef.value);
        const attendanceOption = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          xAxis: {
            type: 'category',
            data: ['正常', '迟到', '早退', '请假', '缺勤']
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: '考勤状态',
              type: 'bar',
              data: [
                attendanceStatusCount.on_time,
                attendanceStatusCount.late,
                attendanceStatusCount.early_departure,
                attendanceStatusCount.leave,
                attendanceStatusCount.absent
              ],
              itemStyle: {
                color: function(params) {
                  const colorList = ['#67C23A', '#F56C6C','#E6A23C','#909399', '#409EFF'];
                  return colorList[params.dataIndex];
                }
              }
            }
          ]
        };
        attendanceChart.setOption(attendanceOption);
      }
    }
    const response2 = await axios.get(`/api/admin/leave-applications`);
    const LeaveApplications = response2.data;
    if (LeaveApplications && Array.isArray(LeaveApplications)) {
      const leaveStatusCount = {};
      LeaveApplications.forEach(app => {
        if (!leaveStatusCount[app.leaveType]) {
          leaveStatusCount[app.leaveType] = 0;
        }
        leaveStatusCount[app.leaveType]++;
      });
      if (leaveChartRef.value) {
        const leaveChart = echarts.init(leaveChartRef.value);
        const leaveOption = {
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: Object.keys(leaveStatusCount)
          },
          series: [
            {
              name: '请假类型',
              type: 'pie',
              radius: '50%',
              data: Object.keys(leaveStatusCount).map(key => ({
                name: key,
                value: leaveStatusCount[key]
              })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        };
        leaveChart.setOption(leaveOption);
      }
    }
  } catch (error) {
    console.error('获取数据或初始化图表失败', error);
  }
});

</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.dashboard-card {
  height: 150px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}

.number {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.description {
  margin-top: 10px;
  color: #909399;
}

.chart-container {
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.placeholder-chart {
  color: #909399;
  font-size: 16px;
}
</style>