<template>
  <div class="face-data-collection">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>人脸数据采集</span>
          <div class="camera-controls">
            <el-button
              type="primary"
              :disabled="isCameraOn"
              @click="startCamera"
            >
              打开摄像头
            </el-button>
            <el-button
              type="danger"
              :disabled="!isCameraOn"
              @click="stopCamera"
            >
              关闭摄像头
            </el-button>
          </div>
        </div>
      </template>

      <div class="collection-container">
        <div class="video-container">
          <div v-if="isCameraOn" class="camera-feed-container">
            <img 
              ref="videoRef"
              class="camera-feed"
              :src="videoStreamUrl"
              alt="Video stream"
            />
          </div>
          <div v-else class="camera-placeholder">
            请点击"打开摄像头"按钮打开摄像头
          </div>
        </div>

        <div class="form-container" style="margin-left: 95px;">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="100px"
          >
            <el-form-item label="工号" prop="employeeId">
              <el-input
                v-model="form.employeeId"
                placeholder="请输入工号"
              />
            </el-form-item>
          </el-form>
          <el-button
            type="primary"
            :disabled="!form.employeeId"
            @click="handleStartCollection"
            style="margin-left: 20px;"
          >
            开始采集
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'

const videoRef = ref(null)
const formRef = ref(null)
const videoStreamUrl = ref('')
const isCameraOn = ref(false)

const form = ref({
  employeeId: ''
})

const rules = {
  employeeId: [{ required: true, message: '请输入工号', trigger: 'change' }]
}

const handleStartCollection = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (!isCameraOn.value) {
        ElMessage.warning('请先打开摄像头再进行采集')
        return
      }
      try {
        const response = await axios.post('/api/attendace/start_capture', {
          folder_name: form.value.employeeId
        })
        if (response.status === 200 && response.data.success) {
          ElMessage.success(response.data.message)
          const intervalId = setInterval(async () => {
            const statusResponse = await axios.get('/api/attendace/check_capture_status')
            if (statusResponse.data.success) {
              clearInterval(intervalId)
              ElMessage.success('人脸数据采集完成')
              stopCamera(false)  
            }
          }, 1000)
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('采集失败:', error)
        ElMessage.error('采集失败，请稍后重试')
      }
    }
  })
}

const startCamera = () => {
  isCameraOn.value = true
  videoStreamUrl.value = 'http://localhost:5000/attendace/video'
  ElMessage.success('摄像头已打开')
}

const stopCamera = (showMessage = true) => {
  isCameraOn.value = false
  videoStreamUrl.value = ''
  if (videoRef.value) {
    videoRef.value.src = ''
    if (videoRef.value.srcObject) {
      const tracks = videoRef.value.srcObject.getTracks()
      tracks.forEach(track => {
        track.stop()
        track.enabled = false
      })
      videoRef.value.srcObject = null
    }
    videoRef.value.load()
    videoRef.value.removeAttribute('src')
  }
  if (showMessage) {
    ElMessage.info('摄像头已关闭')
  }
}

onUnmounted(() => {
  stopCamera(false)
})

onBeforeRouteLeave(() => {
  stopCamera(false)
})

</script>

<style scoped>
.face-data-collection {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.collection-container {
  display: flex;
  flex-direction: column;
  gap: 50px;
}

.video-container {
  flex: 1;
}

.video {
  width: 100%;
  max-width: 640px;
  height: auto;
  background-color: #000;
}

.form-container {
  display: flex;
  align-items: flex-start;
  max-width:600px;
  margin: 0 auto;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.camera-controls {
  display: flex;
  gap: 10px;
}

.camera-feed-container {
  width: 100%;
  max-width: 800px;
  height: 450px;
  background-color: #000;
  overflow: hidden;
  margin: 0 auto;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-placeholder {
  width: 100%;
  max-width: 800px;
  height: 450px;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #909399;
  font-size: 14px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  margin: 0 auto;
}
</style>