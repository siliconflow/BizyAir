<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { uploadImage } from '@/api/public'

const editor = ref<any>(null)
const vditor = ref<Vditor | null>(null)
// const isFullscreen = ref(false)

onMounted(() => {
  vditor.value = new Vditor('vditor', {
    height: 400,
    mode: 'ir',
    theme: 'dark',
    lang: 'en_US',
    placeholder: 'Please input content...',
    fullscreen: {
      index: 999999, // 确保全屏时在最上层
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
      // 'inline-code',
      // 'insert-before',
      // 'insert-after',
      '|',
      'upload',
      'table',
      // '|',
      // 'undo',
      // 'redo',
      // '|',
      'fullscreen',
      // 'edit-mode',
      // {
      //   name: 'more',
      //   toolbar: [
      //     'both',
      //     'code-theme',
      //     'content-theme',
      //     'export',
      //     'outline',
      //     'preview',
      //     'devtools',
      //     'info',
      //     'help',
      //   ],
      // },
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
                vditor.value.tip('Maximum 3 files allowed at once', 3000)
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
                    // console.warn(`File ${file.name} upload failed, remaining retries: ${retryCount}`)
                    if (retryCount === 0) {
                      if (vditor.value) {
                        vditor.value.tip(`File ${currentIndex + 1} upload failed`, 1500)
                      }
                      console.error(`File ${file.name} upload failed permanently:`, err)
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
                vditor.value.tip('Some file failed to upload', 3000)
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
      // linkToImgUrl: '/bizyair/community/files/upload',
      // linkToImgCallback: (responseText: string) => {
      //   console.log('responseText', responseText)
      // }
    },

    after: () => {
      // Callback after editor initialization
      document.querySelector('#vditor')?.classList.add('vditor-dark')

      // 添加事件监听器来阻止删除键事件冒泡
      const editor = document.querySelector('#vditor')
      editor?.addEventListener('keydown', (e: Event) => {
        if ((e as KeyboardEvent).key === 'Backspace' || (e as KeyboardEvent).key === 'Delete') {
          e.stopPropagation()  // 阻止事件冒泡
        }
      }, true)
    }
  })
})
</script>

<template>
  <div id="vditor" ref="editor"></div>
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
  width: 100vw !important;
  height: 100vh !important;
  z-index: 999999 !important;
}

#vditor {
  width: 100%;
  height: 100%;
}
</style>