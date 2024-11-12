<script setup lang="ts">
import MarkDown from '@/components/easy-mark/markDown.js'
import { onMounted } from 'vue'

import '@/components/easy-mark/easymarked.mini.css'

const props = defineProps<{
  modelValue?: string,
  editorId: string
}>()


const initEditor = () => {
  new MarkDown({
    containerId: `${props.editorId}`
  })
}

onMounted(() => {
  initEditor()
})


</script>

<template>
  <div ref="vditorContainer" id="vditor-container">
    <div class="vditor-wrapper" id="vditor-wrapper">
      <div :id="editorId" ref="editor" class="editor"></div>
    </div>
  </div>
</template>