<script setup lang="ts">
import MarkDown from '@/components/easy-mark/markDown.js'
import { onMounted, ref } from 'vue'

import '@/components/easy-mark/easymarked.mini.css'

const props = defineProps<{
  modelValue?: string,
  editorId: string
}>()

const emit = defineEmits(['modelValue', 'isUploading'])

const markdownEditor = ref<MarkDown>()

const initEditor = () => {
  markdownEditor.value = new MarkDown({
    containerId: `${props.editorId}`,
    onUploadStatusChange: (status: boolean) => {
      emit('isUploading', status)
    }
  })

  markdownEditor.value?.easyMDE.codemirror.on("change", () => {
    emit('modelValue', markdownEditor.value?.easyMDE.value())
  })


}

onMounted(() => {
  initEditor()
})

</script>

<template>
  <div :id="editorId" ref="editor" class="editor h-[500px] w-full"></div>
</template>
