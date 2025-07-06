<template>
  <div class="face-recognition">
    <el-card class="camera-card">
      <template #header>
        <div class="card-header">
          <span>人脸识别考勤</span>
          <div class="header-controls">
            <el-button 
              type="success" 
              :disabled="isCameraOn"
              @click="startCamera"
              size="small"
            >
              打开摄像头
            </el-button>
            <el-button 
              type="danger" 
              :disabled="!isCameraOn"
              @click="stopCamera"
              size="small"
            >
              关闭摄像头
            </el-button>
            <el-button 
              type="primary" 
              @click="goBack" 
              size="small"
            >
              返回首页
            </el-button>
          </div>
        </div>
      </template>

      <div class="camera-container">
        <div class="timestamp">
          <div class="date">{{ dateStr }}</div>
          <div class="time">{{ timeStr }}</div>
        </div>
        <template v-if="isCameraOn">
          <img 
            ref="videoRef"
            class="camera-feed"
            :src="videoStreamUrl"
            alt="Video stream"
          />
        </template>
        <el-empty
          v-else
          class="camera-placeholder"
          :image-size="100"
          description="点击“打开摄像头”按钮开启摄像头"
        >
          <template #image>
            <el-icon :size="100" color="#409EFF"><VideoCamera /></el-icon>
          </template>
        </el-empty>
      </div>

      <div class="action-container">
        <el-button 
          type="primary" 
          :loading="isProcessing"
          @click="startRecognition"
          size="large"
        >
          开始签到
        </el-button>
        <el-button 
          type="primary" 
          :loading="isProcessing"
          @click="startDeparture"
          size="large"
        >
          开始签退
        </el-button>
      </div>
    </el-card>

    <el-dialog
      v-model="showResult"
      :title="resultDialogTitle"
      width="30%"
      :show-close="false"
      :close-on-click-modal="false"
    >
      <div class="result-content">
        <el-icon :size="48" :class="resultIconClass">
          <component :is="resultIcon" />
        </el-icon>
        <p>{{ resultMessage }}</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleResultConfirm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, markRaw } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { CircleCheckFilled, CircleCloseFilled, VideoCamera } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const videoRef = ref(null)
const isProcessing = ref(false)
const showResult = ref(false)
const resultDialogTitle = ref('')
const resultMessage = ref('')
const resultIcon = ref(markRaw(CircleCheckFilled))
const resultIconClass = ref('')
const videoStreamUrl = ref('')
const dateStr = ref('')
const timeStr = ref('')
const isCameraOn = ref(false)

const goBack = () => {
  router.push('/')
}

const startCamera = () => {
  isCameraOn.value = true
  videoStreamUrl.value = 'http://localhost:5000/attendace/video_feed'
  ElMessage.success({
    message: '🎥 摄像头已开启',
    customClass: 'camera-message',
    duration: 1500,
    offset: 80
  })
}

const stopCamera = (showMessage = true) => {
  isCameraOn.value = false
  videoStreamUrl.value = ''
  if (videoRef.value) videoRef.value.src = ''
  if (showMessage) ElMessage.info('摄像头已关闭')
}
onUnmounted(() => stopCamera(false))
onBeforeRouteLeave(() => stopCamera(false))
const startRecognition = async () => {
  if (isProcessing.value) return
  if (!isCameraOn.value) {
    ElMessage.warning({
      message: '⚠️ 请先打开摄像头再进行考勤',
      duration: 2000,
      offset: 80,
      customClass: 'camera-message'
    })
    return
  }
  isProcessing.value = true
  try {
    const response = await fetch('http://localhost:5000/attendace/check_integration', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const data = await response.json()
    showRecognitionResult(response.status === 200, data.message)
  } catch (error) {
    console.error('识别失败:', error)
    showRecognitionResult(false, '系统错误，请重试')
  } finally {
    isProcessing.value = false
  }
}
const startDeparture = async () => {
  if (isProcessing.value) return
  if (!isCameraOn.value) {
    ElMessage.warning({
      message: '⚠️ 请先打开摄像头再进行考勤',
      duration: 2000,
      offset: 80,
      customClass: 'camera-message'
    })
    return
  }

  isProcessing.value = true

  try {
    const response = await fetch('http://localhost:5000/attendace/check_departure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const data = await response.json()
    showRecognitionResult(response.status === 200, data.message)
  } catch (error) {
    console.error('识别失败:', error)
    showRecognitionResult(false, '系统错误，请重试')
  } finally {
    isProcessing.value = false
  }
}
const showRecognitionResult = (success, message) => {
  resultDialogTitle.value = success ? '考勤成功' : '考勤失败'
  resultMessage.value = message
  resultIcon.value = success ? markRaw(CircleCheckFilled) : markRaw(CircleCloseFilled)
  resultIconClass.value = success ? 'success-icon' : 'error-icon'
  showResult.value = true
}
const handleResultConfirm = () => {
  showResult.value = false
  if (resultIcon.value === CircleCheckFilled) router.push('/')
}
const updateDateTime = () => {
  const now = new Date()
  dateStr.value = now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  }).replace(/\//g, '-')
  timeStr.value = now.toTimeString().substring(0, 8)
}

onMounted(() => {
  updateDateTime()
  const timer = setInterval(updateDateTime, 1000)
  onUnmounted(() => clearInterval(timer))
})
</script>

<style scoped>
.face-recognition {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.camera-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
}

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  background-color: #000;
  overflow: hidden;
  border-radius: 8px;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  border: 2px dashed #dcdfe6;
}

.action-container {
  margin-top: 24px;
  text-align: center;
  display: flex;
  gap: 20px;
  justify-content: center;
}

.timestamp {
  position: absolute;
  top: 15px;
  right: 15px;
  color: white;
  z-index: 10;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
  font-family: Arial, sans-serif;
}

.timestamp .date {
  font-size: 18px;
  margin-bottom: 4px;
}

.timestamp .time {
  font-size: 32px;
  font-weight: 500;
}

.success-icon {
  color: #67C23A;
}

.error-icon {
  color: #F56C6C;
}

.el-button--large {
  padding: 12px 32px;
  font-size: 16px;
  letter-spacing: 1px;
}
</style>

<style>
.el-message.camera-message {
  background: rgba(25, 25, 25, 0.9) !important;
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
  backdrop-filter: blur(10px);
  color: #fff;
  border-radius: 12px;
  padding: 14px 20px;
}
</style>