<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
          <el-button type="primary" @click="handleEdit">编辑</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        :disabled="!isEditing"
      >
        <el-form-item label="工号" prop="employeeId">
          <el-input v-model="form.employeeId" disabled />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>

        <el-form-item label="部门" prop="department">
          <el-input v-model="form.department" disabled />
        </el-form-item>

        <el-form-item label="职位" prop="position">
          <el-input v-model="form.position" disabled />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>

        <el-form-item v-if="isEditing">
          <el-button type="primary" @click="handleSave">保存</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="password-card">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>

      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleChangePassword">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const formRef = ref(null)
const passwordFormRef = ref(null)
const isEditing = ref(false)

const form = ref({
  employeeId: '',
  name: '',
  department: '',
  position: '',
  phone: '',
  email: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleEdit = () => {
  isEditing.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await axios.put(`/api/employee/update_employee/${form.value.employeeId}`, {
          name: form.value.name,
          phone: form.value.phone,
          email: form.value.email
        })
        if (response.data.message === '更新成功') {
          ElMessage.success('保存成功')
          isEditing.value = false
        }
      } catch (error) {
        ElMessage.error('保存失败')
        console.error('Error updating employee info:', error)
      }
    }
  })
}

const handleCancel = () => {
  isEditing.value = false
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const response = await axios.put('/api/employee/change_password', {
          employeeId: form.value.employeeId,
          oldPassword: passwordForm.value.oldPassword,
          newPassword: passwordForm.value.newPassword
        })
        if (response.data.message === '密码修改成功') {
          ElMessage.success('密码修改成功')
          passwordForm.value = {
            oldPassword: '',
            newPassword: '',
            confirmPassword: ''
          }
        }
      } catch (error) {
        ElMessage.error('密码修改失败')
        console.error('Error changing password:', error)
      }
    }
  })
}

onMounted(async () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    const userInfo = JSON.parse(storedUserInfo)
    try {
      const response = await axios.get(`/api/employee/get_employee/${userInfo.username}`)
      if (response.data) {
        form.value = {
          employeeId: response.data.employee_id,
          name: response.data.employee_name,
          department: response.data.department,
          position: response.data.job_title,
          phone: response.data.phone_number,
          email: response.data.email
        }
      }
    } catch (error) {
      ElMessage.error('获取员工信息失败')
      console.error('Error fetching employee info:', error)
    }
  }
})

</script>

<style scoped>
.profile-container {
  padding: 20px;
  display: flex;
  gap: 20px;
}

.profile-card {
  flex: 2;
}

.password-card {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 