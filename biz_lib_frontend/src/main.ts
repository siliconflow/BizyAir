import { createApp, App as VueApp } from 'vue'
import './assets/index.css'
import App from './App.vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'

let app: VueApp | null = null

// 修改 mount 方法接收 props
export function mount(container: string | Element,comfyUIApp?: any, props = {}) {
  if (app) {
    console.warn('应用已经挂载，请先卸载后再重新挂载')
    return
  }
  const mergedProps = {
    ...props,
    comfyUIApp
  }

  app = createApp(App, mergedProps)
  app.component('font-awesome-icon', FontAwesomeIcon)
  library.add(fas)
  app.provide('comfyUIApp', comfyUIApp);
  app.mount(container)
  return app
}

// 导出卸载方法
export function unmount() {
  if (!app) {
    console.warn('应用尚未挂载，无需卸载')
    return
  }
  app.unmount()
  app = null
}

// 如果是直接运行而不是作为库使用，则自动挂载
if (import.meta.env.MODE !== 'production') {
  mount('#app')
}
