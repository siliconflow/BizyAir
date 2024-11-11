import { createApp } from 'vue'
import { Toaster } from '@/components/ui/sonner'
export function useToaster() {
  let container: HTMLDivElement | null

  if (document.querySelector('#bizyair-toaster')) {
    container = document.querySelector('#bizyair-toaster')
  } else {
    container = document.createElement('div')
    container.id = 'bizyair-toaster'
    document.body.appendChild(container)
  }
  container && (container.style.display = 'none')
  const app = createApp(Toaster, { class: 'h-20', 'data-y-position': 'top', 'data-x-position': 'right' })

  if (container) {
    app.mount(container)
  }
}
