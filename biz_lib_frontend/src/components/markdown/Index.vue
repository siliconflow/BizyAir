<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { uploadImage } from '@/api/public'
const editor = ref<any>(null)
const vditor = ref<Vditor | null>(null)
const vditorContainer = ref<HTMLElement | null>(null)
const isFullscreen = ref(false)

const showOriginalEditor = ref(true)
const editorContent = ref('')


const vditorConfig: IOptions = {
  height: 400,
  mode: 'ir',
  theme: 'dark',
  lang: 'en_US',
  placeholder: '请输入内容...',
  fullscreen: {
    index: 999999999,
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
    'table',
    {
      name: 'fullscreen',
      tip: '全屏',
      click: (e: Event) => {
        e.stopPropagation()
        isFullscreen.value = !isFullscreen.value
        if (isFullscreen.value) {
          moveEditorToBody()
        } else {
          moveEditorBackToContainer()
        }
      }
    }  // 直接添加 fullscreen 按钮
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
          // 限制最多上传3个文件
          if (files.length > 3) {
            if (vditor.value) {
              vditor.value.tip('一次最多上传3个文件', 3000)
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
                    vditor.value.tip(`正在上传文件 ${currentIndex + 1}/${files.length}...`, 1500)
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
                      vditor.value.tip(`文件 ${currentIndex + 1} 上传失败`, 1500)
                    }
                    console.error(`文件 ${file.name} 上传失败:`, err)
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
                        您的浏览器不支持 video 标签。
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
              vditor.value.tip('部分文件上传失败', 3000)
            }
            resolve('')
          })

        } catch (error) {
          if (vditor.value) {
            vditor.value.tip('图片上传失败，请重试', 3000)
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
    document.querySelector('#vditor')?.classList.add('vditor-dark')

    const editor = document.querySelector('#vditor')
    editor?.addEventListener('keydown', (e: Event) => {
      if ((e as KeyboardEvent).key === 'Backspace' || (e as KeyboardEvent).key === 'Delete') {
        e.stopPropagation()
      }
    }, true)
  }

}
const moveEditorToBody = () => {
  const vditorEl = document.querySelector('#vditor') || document.querySelector('#vditor-fullscreen')
  if (vditorEl) {
    document.body.appendChild(vditorEl)
  }
}

const moveEditorBackToContainer = () => {
  const vditorEl = document.querySelector('#vditor')
  const container = vditorContainer.value
  if (vditorEl && container) {
    container.appendChild(vditorEl)
  }
}

onMounted(() => {
  vditor.value = new Vditor('vditor', {
    ...vditorConfig,
    after: () => {
      document.querySelector('#vditor')?.classList.add('vditor-dark')
      const editor = document.querySelector('#vditor')
      editor?.addEventListener('keydown', (e: Event) => {
        if ((e as KeyboardEvent).key === 'Backspace' || (e as KeyboardEvent).key === 'Delete') {
          e.stopPropagation()
        }
      }, true)
    }
  })
})


</script>

<template>
  <div class="vditor-wrapper" ref="vditorContainer">
    <div id="vditor" ref="editor" v-if="showOriginalEditor"></div>
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

.vditor-fullscreen {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  transform: none !important;
  margin: 0 !important;
  padding: 20px !important;
  background: var(--vditor-bg-color);
  border-radius: 0;
  box-shadow: none;
  z-index: 99999 !important;
}

.vditor-fullscreen .vditor-toolbar {
  width: 100% !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 2 !important;
}

.vditor-fullscreen .vditor-content {
  height: calc(100% - 40px) !important;
  overflow: auto !important;
}

.vditor-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

/* 适配 ComfyUI 容器 */
.comfyui-container .vditor-fullscreen {
  position: fixed !important;
}

.vditor-fullscreen-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99999;
  background: var(--vditor-bg-color);
}

#vditor-fullscreen {
  height: 100vh;
}
</style>