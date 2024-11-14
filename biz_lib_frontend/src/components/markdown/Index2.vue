<template>
  <MdEditor
    :editorId="editorId"
    v-model="text"
    theme="dark"
    :toolbars="toolbar"
    ref="editorRef"
    @input="handleInput"
    @on-upload-img="handleUploadImg">
    <template #defToolbars>
      <NormalToolbar title="fullscreen" @onClick="handleFullClick">
        <template #trigger>
          <Maximize class='w-4 h-4 mt-1' />
        </template>
      </NormalToolbar>
    </template>
  </MdEditor>
  <!--
    language="en-US" -->
  <Teleport to="body" v-if='isFullscreen'>
    <MdEditor
      v-model="text"
      theme="dark"
      :editorId="`full-${editorId}`"
      :toolbars="toolbar"
      :pageFullscreen="true"
      class="fixed top-0 left-0 w-[100vw] h-[100vh] z-12000"

      @input="handleInput"
      @on-upload-img="handleUploadImg">
      <template #defToolbars>
        <NormalToolbar title="fullscreen" @onClick="handleFullClick">
          <template #trigger>
            <Maximize class='w-4 h-4 mt-1' />
          </template>
        </NormalToolbar>
      </template>
    </MdEditor>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue';
import screenfull from 'screenfull';
import highlight from 'highlight.js';
import prettier from 'prettier';
import cropper from 'cropperjs';
import { uploadImage } from '@/api/public'
import { MdEditor, config, NormalToolbar } from 'md-editor-v3';

import { Maximize } from 'lucide-vue-next';

import 'md-editor-v3/lib/style.css';


const toolbar = [
  'bold', 'italic', 'underline', 'title', '-',
  'quote', 'code', 'table', 'image', '-',
  'mermaid', 'katex', '-',
  'link', '=',
  'preview',
  0
];
const isFullscreen = ref(false);
const handleFullClick = () => {
  isFullscreen.value = !isFullscreen.value;
  if (isFullscreen.value) {
    screenfull.request();
    document.querySelector('[role="dialog"]').style.display = 'none';
  } else {
    screenfull.exit();
    document.querySelector('[role="dialog"]').style.display = 'block';
  }
};
const props = defineProps({
  editorId: String,
  modelValue: String,
})
const text = ref(props.modelValue);
const emit = defineEmits(['update:modelValue', 'isUploading'])
const handleInput = () => {
  emit('update:modelValue', text)
};
const handleUploadImg = async (file, callback) => {
  const res = await uploadImage(file[0]);
  callback([res.data.url])
};
const editorRef = ref(null);

config({
  editorExtensions: {
    highlight: {
      instance: highlight,
    },
    prettier: {
      prettierInstance: prettier,
    },
    cropper: {
      instance: cropper,
    },
    screenfull: {
      instance: screenfull,
    },
  },
});
// onMounted(() => {
//   console.log(mdEditorFull.value.toggleFullscreen)
//   mdEditorFull.value.toggleFullscreen();
// });
</script>
<style scoped>
:deep(.md-editor-toolbar-item svg.md-editor-icon) {
  @apply w-6 h-6;
}
</style>
