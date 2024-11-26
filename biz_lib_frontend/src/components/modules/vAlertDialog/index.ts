import { createApp, h } from 'vue'
import AlertDialog from './index.vue'

export function useAlertDialog(options: { title?: string; desc?: string; cancel?: string; continue?: string; z?: string;}) {
  return new Promise((resolve) => {
    const container = document.createElement('div')
    container.className = 'shadcn-root'
    document.body.appendChild(container)

    const app = createApp({
      render() {
        return h(AlertDialog, {
          ...options,
          onContinueClick: () => {
            resolve(true)
            app.unmount()
            document.body.removeChild(container)
          },
          onCancelClick: () => {
            resolve(false)
            app.unmount()
            document.body.removeChild(container)
          }
        })
      }
    })

    app.mount(container)
  })
}
