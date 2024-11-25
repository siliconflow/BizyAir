import { createApp } from 'vue'
import Toaster from './index.vue'

export function useToaster(options: { [x: string]: unknown; } | string) {
  let containerBox:HTMLDivElement
  if (document.querySelector('.bizyair-toaster-container')) {
    containerBox = document.querySelector('.bizyair-toaster-container') as HTMLDivElement
  } else {
    containerBox = document.createElement('div')
    containerBox.className = 'bizyair-toaster-container shadcn-root'
  }
  containerBox.style.position = 'fixed'
  containerBox.style.zIndex = '12002'
  containerBox.style.top = '8px'
  containerBox.style.width = '400px'
  if (typeof options === 'string') {
    options = { message: options, type: 'info', position: 'right' }
  }
  options.position = options.position || 'right'
  if (options.position === 'left') {
    containerBox.style.left = '8px'
  }
  if (options.position === 'right') {
    containerBox.style.right = '8px'
  }
  if (options.position === 'center') {
    containerBox.style.left = '50%'
    containerBox.style.transform = 'translateX(-50%)'
  }
  document.body.appendChild(containerBox)


  const container = document.createElement('div')
  container.style.transition = 'all 0.3s'
  containerBox.appendChild(container)

  const app = createApp(Toaster, {
    ...options,
    onClose: () => {
      app.unmount()
      containerBox.removeChild(container)
    }
  })

  if (container) {
    app.mount(container)
  }
}
useToaster.warning = (message: string) => {
  useToaster({
    message,
    type: 'warning'
  })
}


useToaster.success = (message: string) => {
  useToaster({
    message,
    type: 'success'
  })
}
useToaster.error = (message: string) => {
  useToaster({
    message,
    type: 'error'
  })
}
