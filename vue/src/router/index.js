import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue')
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      children: [
        {
          path: 'dashboard',
          name: 'AdminDashboard',
          component: () => import('../views/admin/Dashboard.vue'),
          meta: { requiresAuth: true, role: 'admin' }
        },
        {
          path: 'employee',
          name: 'EmployeeManagement',
          component: () => import('../views/admin/EmployeeManagement.vue')
        },
        {
          path: 'surgery',
          name: 'SurgeryNotification',
          component: () => import('../views/admin/SurgeryNotification.vue')
        },
        {
          path: 'attendance',
          name: 'AttendanceRecords',
          component: () => import('../views/admin/AttendanceRecords.vue')
        },
        {
          path: 'leave',
          name: 'LeaveApproval',
          component: () => import('../views/admin/LeaveApproval.vue')
        },
        {
          path: 'face',
          name: 'FaceDataCollection',
          component: () => import('../views/admin/FaceDataCollection.vue')
        }
      ]
    },
    {
      path: '/staff',
      name: 'Staff',
      component: () => import('../views/staff/StaffLayout.vue'),
      children: [
        {
          path: 'dashboard',
          name: 'staff-dashboard',
          component: () => import('../views/staff/Dashboard.vue'),
          meta: { requiresAuth: true, role: 'staff' }
        },
        {
          path: 'profile',
          name: 'StaffProfile',
          component: () => import('../views/staff/Profile.vue')
        },
        {
          path: 'surgery',
          name: 'StaffSurgery',
          component: () => import('../views/staff/SurgeryNotification.vue')
        },
        {
          path: 'attendance',
          name: 'StaffAttendance',
          component: () => import('../views/staff/Attendance.vue')
        },
        {
          path: 'leave',
          name: 'StaffLeave',
          component: () => import('../views/staff/Leave.vue')
        }
      ]
    },
    {
      path: '/staff/face-recognition',
      name: 'face-recognition',
      component: () => import('../views/staff/FaceRecognition.vue')
    }
  ]
})
router.beforeEach((to, from, next) => {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  const publicRoutes = ['home', 'face-recognition']
  if (!publicRoutes.includes(to.name)) {
    if (!userInfo || !userInfo.userType) {
      next({ name: 'home' })
      return
    }
    if (to.meta.role && to.meta.role !== userInfo.userType) {
      next({ name: userInfo.userType === 'admin' ? 'admin-dashboard' : 'staff-dashboard' })
      return
    }
  }
  next()
})
export default router