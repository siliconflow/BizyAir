import { createApp, h } from 'vue'
import Shadet from './index.vue'

export function useShadet(options: { content?: string; z?: string;}) {
  const container = document.createElement('div')
  container.className = 'shadcn-root'
  document.body.appendChild(container)
  const app = createApp({
    render() {
      return h(Shadet, {
        ...options
      })
    }
  })
  app.mount(container)
  function close() {
    app.unmount()
    document.body.removeChild(container)
  }
  return {
    close
  }
}
