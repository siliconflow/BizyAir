import { createApp } from 'vue'
import './assets/index.css'
import App from './App.vue'
import { createPinia } from 'pinia';
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
  app.directive('debounce', {
    mounted(el, binding) {
      let timer:any = null
      el.addEventListener('keyup', () => {
        if (timer) clearTimeout(timer)
        timer = setTimeout(() => {
          binding.value()
        },(binding.arg as unknown) as number || 500)
      })
    },
    unmounted(el,binding) {
      if(binding){
        el.removeEventListener('keyup', binding.value)
      }
    }
  })

  const instance = app.mount(container);
  return {
    instance
  };
}

let app = createApp(App)
app.use(createPinia())
// 修改 mount 方法接收 props
export function mount(container: string | Element,comfyUIApp?: any) {
  // console.log('mount', container, comfyUIApp, props)
  // if (app) {
  //   console.warn('应用已经挂载，请先卸载后再重新挂载')
  //   return
  // }

  app.provide('comfyUIApp', comfyUIApp);
  app.mount(container)
  // return app
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
