<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { uploadImage } from '@/api/public'

const props = defineProps<{
  modelValue?: string,
  editorId: string 
}>()

const editor = ref<any>(null)
const vditor = ref<Vditor | null>(null)
const vditorContainer = ref<HTMLElement | null>(null)
const isFullscreen = ref(false)
const showOriginalEditor = ref(true)
const emit = defineEmits(['update:modelValue'])

const vditorConfig: IOptions = {
  height: 400,
  mode: 'ir',
  theme: 'dark',
  cache: {
    enable: false
  },
  lang: 'en_US',
  placeholder: 'Please enter content...',
  fullscreen: {
    index: 9999
  },
  input: (value: string) => {
    emit('update:modelValue', value)
  },
  toolbar: [
    'emoji',
    'headings',
    'bold',
    'italic',
    'strike',
    'link',
    '|',
    'list',
    'ordered-list',
    'check',
    'outdent',
    'indent',
    '|',
    'quote',
    'line',
    'code',
    '|',
    'upload',
    {
      name: 'fullscreen',
      tip: 'Fullscreen',
      click: () => {
        isFullscreen.value = !isFullscreen.value
        if (isFullscreen.value) {
          moveEditorToBody()
        } else {
          moveEditorBackToContainer()
        }
      }
    }
  ],
  upload: {
    url: '/bizyair/community/files/upload',
    max: 20 * 1024 * 1024,
    accept: 'image/*, video/*',
    multiple: true,
    fieldName: 'file',
    extraData: {
      platform: 'vditor'
    },
    handler: (files: File[]): Promise<string> => {
      return new Promise((resolve) => {
        try {
          if (files.length > 3) {
            if (vditor.value) {
              vditor.value.tip('Maximum 3 files can be uploaded at once', 3000)
            }
            resolve('')
            return
          }

          const batchSize = 3
          const batches: File[][] = []
          for (let i = 0; i < files.length; i += batchSize) {
            batches.push(files.slice(i, i + batchSize))
          }
          const processBatch = async (batch: File[], startIndex: number) => {
            const results = []
            for (let index = 0; index < batch.length; index++) {
              const file = batch[index]
              const currentIndex = startIndex + index
              let retryCount = 3
              while (retryCount > 0) {
                try {
                  const response = await uploadImage(file)
                  if (vditor.value) {
                    vditor.value.tip(`Uploading file ${currentIndex + 1}/${files.length}...`, 1500)
                  }
                  results.push({
                    success: true,
                    fileName: file.name,
                    imageUrl: response.data.url
                  })
                  break
                } catch (err) {
                  retryCount--
                  if (retryCount === 0) {
                    if (vditor.value) {
                      vditor.value.tip(`File ${currentIndex + 1} upload failed`, 1500)
                    }
                    console.error(`File ${file.name} upload failed:`, err)
                  } else {
                    await new Promise(resolve => setTimeout(resolve, 1000))
                  }
                }
              }
            }
            return results
          }
          const processAllBatches = async () => {
            let allResults: any[] = []
            for (let i = 0; i < batches.length; i++) {
              const results = await processBatch(batches[i], i * batchSize)
              allResults = allResults.concat(results)
            }
            if (allResults.length > 0 && vditor.value) {
              const markdownContent = allResults
                .map(result => {
                  if (result.fileName.match(/\.(mp4|webm|ogg)$/i)) {
                    return `<video src="${result.imageUrl}" controls>
                        Your browser does not support the video tag.
                      </video>`
                  } else {
                    return `![${result.fileName}](${result.imageUrl})`
                  }
                })
                .join('\n')
              vditor.value.insertValue(markdownContent)
            }
            resolve('')
          }
          processAllBatches().catch(_ => {
            if (vditor.value) {
              vditor.value.tip('Some files failed to upload', 3000)
            }
            resolve('')
          })

        } catch (error) {
          if (vditor.value) {
            vditor.value.tip('Image upload failed, please try again', 3000)
          }
          resolve('')
        }
      })
    },
    filename: (name: string) => {
      return `${Date.now()}-${name}`
    },
  },

  after: () => {
    document.querySelector(`#${props.editorId}`)?.classList.add('vditor-dark')
    const editor = document.querySelector(`#${props.editorId}`)
    editor?.addEventListener('keydown', (e: Event) => {
      if ((e as KeyboardEvent).key === 'Backspace' || (e as KeyboardEvent).key === 'Delete') {
        e.stopPropagation()
      }
    }, true)
  }
}

const moveEditorToBody = () => {
  const vditorEl = document.querySelector(`#${props.editorId}`) as HTMLElement
  if (vditorEl) {
    const rect = vditorEl.getBoundingClientRect()
    document.body.appendChild(vditorEl)
    vditorEl.style.position = 'fixed'
    vditorEl.style.left = `${rect.left}px`
    vditorEl.style.top = `${rect.top}px`
    vditorEl.style.width = `${rect.width}px`
    vditorEl.style.height = `${rect.height}px`

    vditorEl.offsetHeight
    vditorEl.style.left = '0'
    vditorEl.style.top = '0'
    vditorEl.style.width = '100vw'
    vditorEl.style.height = '100vh'
    vditorEl.style.zIndex = '99999'
    vditorEl.style.background = 'var(--background)'
    vditorEl.style.transition = 'all 0.3s ease'
    vditorEl.style.margin = '0'
    vditorEl.style.padding = '0'
    vditorEl.style.border = 'none'
  }
}

const moveEditorBackToContainer = () => {
  const vditorEl = document.querySelector(`#${props.editorId}`) as HTMLElement
  const container = vditorContainer.value
  if (vditorEl && container) {
    container.appendChild(vditorEl)

    vditorEl.style.position = 'relative'
    vditorEl.style.left = ''
    vditorEl.style.top = ''
    vditorEl.style.width = '100%'
    vditorEl.style.height = '400px'
    vditorEl.style.zIndex = ''
    vditorEl.style.background = ''
    vditorEl.style.transition = ''
    vditorEl.style.margin = ''
    vditorEl.style.padding = ''
    vditorEl.style.border = ''

    vditorEl.offsetHeight
  }
}

onMounted(() => {
  vditor.value = new Vditor(props.editorId, {
    ...vditorConfig,
    after: () => {
      document.querySelector(`#${props.editorId}`)?.classList.add('vditor-dark')
      const editor = document.querySelector(`#${props.editorId}`)
      editor?.addEventListener('keydown', (e: Event) => {
        if ((e as KeyboardEvent).key === 'Backspace' || (e as KeyboardEvent).key === 'Delete') {
          e.stopPropagation()
        }
      }, true)

      if (props.modelValue) {
        vditor.value?.setValue(props.modelValue)
      }
    }
  })
})

onUnmounted(() => {
  if (isFullscreen.value) {
    moveEditorBackToContainer()
  }
})

</script>

<template>
  <div class="vditor-wrapper" ref="vditorContainer">
    <div :id="editorId" ref="editor" v-if="showOriginalEditor"></div>
  </div>
</template>

<style>
.vditor-dark {
  color: #fff;
}

.vditor-dark .vditor-ir {
  color: #fff;
}

.vditor-dark .vditor-ir pre.vditor-reset {
  color: #fff;
}

.vditor-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

#vditor {
  transition: all 0.2s;
}
</style>