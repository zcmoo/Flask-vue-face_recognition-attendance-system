<template>
  <div class="employee-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>员工管理</span>
          <el-button type="primary" @click="handleAdd">添加员工</el-button>
        </div>
      </template>
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索员工姓名/工号"
          class="search-input"
          clearable
          @keyup.enter="fetchEmployees()"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="departmentFilter" placeholder="选择部门" clearable @change="fetchEmployees()">
          <el-option
            v-for="item in departments"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </div>

      <el-table :data="employees" style="width: 100%">
        <el-table-column prop="employee_id" label="工号" width="100" />
        <el-table-column prop="employee_name" label="姓名" width="120" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="job_title" label="职位" width="120" />
        <el-table-column prop="phone_number" label="联系电话" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="密码" width="120">
          <template #default="scope">
            <span>********</span>
          </template>
        </el-table-column>
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

    <!-- 添加/编辑员工对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加员工' : '编辑员工'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="employeeForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="姓名" prop="employee_name">
          <el-input v-model="employeeForm.employee_name" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-select v-model="employeeForm.department" placeholder="请选择部门">
            <el-option
              v-for="item in departments"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位" prop="job_title">
          <el-input v-model="employeeForm.job_title" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone_number">
          <el-input v-model="employeeForm.phone_number" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="employeeForm.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="employeeForm.password" />
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
import { ref, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';

const searchQuery = ref('');
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

const employeeForm = ref({
  employee_id: null,
  employee_name: '',
  department: '',
  job_title: '',
  phone_number: '',
  email: '',
  password: ''
});

const employees = ref([]);

const rules = {
  employee_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  job_title: [{ required: true, message: '请输入职位', trigger: 'blur' }],
  phone_number: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
};

const handleAdd = () => {
  dialogType.value = 'add';
  employeeForm.value = {
    employee_id: null,
    employee_name: '',
    department: '',
    job_title: '',
    phone_number: '',
    email: '',
    password: ''
  };
  dialogVisible.value = true;
};

const handleEdit = (row) => {
  if (!row) {
    console.error('未提供有效的员工数据');
    return;
  }
  dialogType.value = 'edit';
  employeeForm.value = {
    employee_id: row.employee_id,
    employee_name: row.employee_name,
    department: row.department,
    job_title: row.job_title,
    phone_number: row.phone_number,
    email: row.email,
    password: row.password
  };
  dialogVisible.value = true;
};

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除员工 ${row.employee_name} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    axios.delete(`/api/admin/delete_employee_kq/${row.employee_id}`)
    .then(response => {
        if (response.status === 200) {
          ElMessage.success('删除成功');
          fetchEmployees();
        } else {
          ElMessage.error(response.data.message || '删除失败');
        }
      })
    .catch(error => {
        console.error('删除失败:', error);
        ElMessage.error(`服务器错误: ${error.response?.data.message || '未知错误'}`);
      });
  }).catch(() => {});
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const url = dialogType.value === 'add'
          ? '/api/admin/add_employee_kq'
          : `/api/admin/edit_employee_kq/${employeeForm.value.employee_id}`;
        const method = dialogType.value === 'add' ? 'post' : 'put';
        const response = await axios[method](url, {
          employee_name: employeeForm.value.employee_name,
          department: employeeForm.value.department,
          job_title: employeeForm.value.job_title,
          phone_number: employeeForm.value.phone_number,
          email: employeeForm.value.email,
          password: employeeForm.value.password
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (response.status === 201 || response.status === 200) {
          ElMessage.success(dialogType.value === 'add' ? '员工信息添加成功' : '员工信息编辑成功');
          dialogVisible.value = false;
          fetchEmployees();
        } else {
          ElMessage.error(response.data.message || (dialogType.value === 'add' ? '添加员工信息失败' : '编辑员工信息失败'));
        }
      } catch (error) {
        console.error(dialogType.value === 'add' ? '添加员工信息失败:' : '编辑员工信息失败:', error);
        if (error.response) {
          ElMessage.error(`服务器错误: ${error.response.data.message || '未知错误'}`);
        } else if (error.request) {
          ElMessage.error('无法连接到服务器，请检查网络连接');
        } else {
          ElMessage.error(dialogType.value === 'add' ? '添加员工信息失败，请稍后重试' : '编辑员工信息失败，请稍后重试');
        }
      }
    }
  });
};

const fetchEmployees = async () => {
  try {
    const response = await axios.get('/api/admin/get_employees_kq', {
      params: {
        search: searchQuery.value,
        department: departmentFilter.value,
        page: currentPage.value,
        pageSize: pageSize.value
      }
    });
    employees.value = response.data.items;
    total.value = response.data.total;
  } catch (error) {
    console.error('获取员工列表失败:', error);
    ElMessage.error(`服务器错误: ${error.response?.data.message || '未知错误'}`);
  }
};

const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  fetchEmployees();
};

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
  fetchEmployees();
};

onMounted(() => {
  fetchEmployees();
});
</script>

<style scoped>
.employee-management {
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

.search-input {
  width: 300px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>    