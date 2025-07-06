
//删除无用的导包
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/assets/global.css'
import {zhCn} from "element-plus/es/locale/index";

// 如果您正在使用CDN引入，请删除下面一行。
import * as ElementPlusIconsVue from '@element-plus/icons-vue'



const app = createApp(App)

app.use(router)
app.use(ElementPlus,{
    local:zhCn,//导入中文
})
for (const [key, component] of Object.entries(ElementPlusIconsVue
)) {
    app.
    component
    (key, component)
}
app.mount('#app')


