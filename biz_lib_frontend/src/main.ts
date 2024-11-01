import { createApp, App as VueApp } from 'vue'
import './assets/index.css'
import App from './App.vue'
import VueClipboard from 'vue-clipboard2';
import { ModelSelect } from '@/components/model-select/'


export const showModelSelect = (options: { [x: string]: unknown; } | null | undefined) => {
  const existingContainer = document.getElementById('bizyair-model-select');
  if (existingContainer) {
    document.body.removeChild(existingContainer);
  }
  const container = document.createElement('div');
  container.id = 'bizyair-model-select'
  document.body.appendChild(container);
  const app = createApp(ModelSelect, {
    ...options,
    onClose: () => {
      app.unmount();
      document.body.removeChild(container);
    },
    onClicked: (e: any) => {  
      console.log('clicked', e)
    }
  });
  console.log('showModelSelect', app)
  const instance = app.mount(container);
  return {
    instance
  };
}

let app: VueApp = createApp(App)
app.use(VueClipboard);
// 修改 mount 方法接收 props
export function mount(container: string | Element,comfyUIApp?: any, props = {}) {
  console.log('mount', container, comfyUIApp, props)
  // if (app) {
  //   console.warn('应用已经挂载，请先卸载后再重新挂载')
  //   return
  // }

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
 
}

// 如果是直接运行而不是作为库使用，则自动挂载
if (import.meta.env.MODE !== 'production') {
  mount('#app')
}
