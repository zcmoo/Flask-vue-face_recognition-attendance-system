<template>
  <div class="surgery-notification">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>手术通知管理</span>
          <el-button type="primary" @click="handleAdd">发布通知</el-button>
        </div>
      </template>

      <div class="search-bar">
        <el-date-picker
          v-model="dateFilter"
          type="date"
          placeholder="选择日期"
          clearable
          :disabled-date="disabledDateForSearch"
        />
        <el-select v-model="departmentFilter" placeholder="选择部门" clearable>
          <el-option
            v-for="item in departments"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </div>

      <el-table :data="filteredNotifications" style="width: 100%">
        <el-table-column label="手术日期" width="120">
          <template #default="scope">
            {{ scope.row.surgery_date.split(' ')[0] }}
          </template>
        </el-table-column>
        <el-table-column label="手术时间" width="120">
          <template #default="scope">
            {{ scope.row.surgery_time.split(' ')[1] }}
          </template>
        </el-table-column>
        <el-table-column prop="department" label="科室" width="120" />
        <el-table-column prop="operating_room" label="手术室" width="120" />
        <el-table-column prop="patient_name" label="患者姓名" width="120" />
        <el-table-column prop="surgery_type" label="手术类型" width="120" />
        <el-table-column prop="responsible_doctor_id" label="主刀医生工号" width="120" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button-group>
              <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </el-button-group>
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
      :title="dialogType === 'add'? '发布手术通知' : '编辑手术通知'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="notificationForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="手术日期" prop="surgery_date">
          <el-date-picker
            v-model="notificationForm.surgery_date"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDateForDialog"
          />
        </el-form-item>
        <el-form-item label="手术时间" prop="surgery_time">
          <el-time-picker
            v-model="notificationForm.surgery_time"
            placeholder="选择时间"
            value-format="HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="科室" prop="department">
          <el-select v-model="notificationForm.department" placeholder="请选择科室">
            <el-option
              v-for="item in departments"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="手术室" prop="operating_room">
          <el-input v-model="notificationForm.operating_room" />
        </el-form-item>
        <el-form-item label="患者姓名" prop="patient_name">
          <el-input v-model="notificationForm.patient_name" />
        </el-form-item>
        <el-form-item label="手术类型" prop="surgery_type">
          <el-input v-model="notificationForm.surgery_type" />
        </el-form-item>
        <el-form-item label="主刀医生工号" prop="responsible_doctor_id">
          <el-input v-model="notificationForm.responsible_doctor_id" placeholder="请输入主刀医生工号" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="notificationForm.notes"
            type="textarea"
            :rows="3"
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
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';

const dateFilter = ref('');
const departmentFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const dialogVisible = ref(false);
const dialogType = ref('add');
const formRef = ref(null);

const departments = [
  { value: '外科', label: '外科' },
  { value: '内科', label: '内科' },
  { value: '急诊科', label: '急诊科' },
  { value: '儿科', label: '儿科' }
];

const notificationForm = ref({
  surgery_date: '',
  surgery_time: '',
  department: '',
  operating_room: '',
  patient_name: '',
  surgery_type: '',
  responsible_doctor_id: '',
  notes: ''
});

const rules = {
  surgery_date: [
    { required: true, message: '请选择手术日期', trigger: 'change' },
    { validator: (rule, value, callback) => {
      if (value &&!isNaN(new Date(value).getTime())) {
        callback();
      } else {
        callback(new Error('请输入有效的日期'));
      }
    }, trigger: 'change' }
  ],
  surgery_time: [
    { required: true, message: '请选择手术时间', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const timeRegex = /^\d{2}:\d{2}:\d{2}$/;
      if (value && timeRegex.test(value)) {
        callback();
      } else {
        callback(new Error('请输入有效的时间格式（HH:MM:SS）'));
      }
    }, trigger: 'change' }
  ],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  operating_room: [{ required: true, message: '请输入手术室', trigger: 'blur' }],
  patient_name: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
  surgery_type: [{ required: true, message: '请输入手术类型', trigger: 'blur' }],
  responsible_doctor_id: [{ required: true, message: '请输入主刀医生工号', trigger: 'blur' }]
};

const notifications = ref([]);

const filteredNotifications = computed(() => {
  return notifications.value.filter(notification => {
    const notificationDate = new Date(notification.surgery_date);
    const filterDate = dateFilter.value? new Date(dateFilter.value) : null;
    const notificationDateStr = notificationDate.toISOString().split('T')[0];
    const filterDateStr = filterDate? new Date(filterDate.setDate(filterDate.getDate() + 1)).toISOString().split('T')[0] : '';
    const matchesDate = !filterDateStr || notificationDateStr === filterDateStr;
    const matchesDepartment = !departmentFilter.value || notification.department === departmentFilter.value;
    return matchesDate && matchesDepartment;
  });
});

const disabledDateForSearch = (time) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return time < today;
};

const disabledDateForDialog = (time) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return time < today;
};

const handleAdd = () => {
  dialogType.value = 'add';
  notificationForm.value = {
    surgery_date: '',
    surgery_time: '',
    department: '',
    operating_room: '',
    patient_name: '',
    surgery_type: '',
    responsible_doctor_id: '',
    notes: ''
  };
  dialogVisible.value = true;
};

const handleEdit = (row) => {
  dialogType.value = 'edit';
  const formattedTime = row.surgery_time.split(' ')[1];
  notificationForm.value = {
  ...row,
    surgery_time: formattedTime
  };
  dialogVisible.value = true;
};

const handleDelete = async (row) => {
  await ElMessageBox.confirm(
    `确定要删除手术通知吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/admin/surgery_notifications_kq/${row.notification_id}`);
      ElMessage.success('删除成功');
      await fetchNotifications();
    } catch (error) {
      console.error('删除请求出错:', error);
      ElMessage.error('删除失败，请检查网络或重试');
    }
  }).catch(() => {});
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      const selectedDate = new Date(notificationForm.value.surgery_date);
      const selectedTime = notificationForm.value.surgery_time;
      if (isNaN(selectedDate.getTime())) {
        ElMessage.error('请输入有效的日期');
        return;
      }
      const formattedDate = new Date(selectedDate.setDate(selectedDate.getDate() + 1)).toISOString().split('T')[0];
      const formData = {
      ...notificationForm.value,
        surgery_date: formattedDate,
        surgery_time: `${formattedDate}T${selectedTime}`
      };
      try {
        if (dialogType.value === 'add') {
          await axios.post('/api/admin/surgery_notifications_kq', formData);
          ElMessage.success('发布成功');
        } else {
          await axios.put(`/api/admin/surgery_notifications_kq/${notificationForm.value.notification_id}`, formData);
          ElMessage.success('修改成功');
        }
        dialogVisible.value = false;
        await fetchNotifications();
      } catch (error) {
        console.error('提交请求出错:', error);
        ElMessage.error('操作失败，请检查网络或重试');
      }
    }
  });
};

const fetchNotifications = async () => {
  let formattedDate = dateFilter.value;
  if (formattedDate) {
    formattedDate = new Date(formattedDate).toISOString().split('T')[0];
  }
  try {
    const response = await axios.get('/api/admin/surgery_notifications_kq', {
      params: {
        page: currentPage.value,
        pageSize: pageSize.value,
        date: formattedDate,
        department: departmentFilter.value
      }
    });
    notifications.value = response.data.items.map(item => ({
    ...item,
      surgery_date: item.surgery_date, 
      surgery_time: item.surgery_time 
    }));
    total.value = response.data.total;
  } catch (error) {
    console.error('获取通知请求出错:', error);
    ElMessage.error('获取手术通知失败，请检查网络或重试');
  }
};

const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  fetchNotifications();
};

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
  fetchNotifications();
};

onMounted(() => {
  fetchNotifications();
});
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