<template>
  <MdEditor :editorId="editorId" v-model="text" theme="dark" :toolbars="toolbar" ref="editorRef" :autoDetectCode="true"
    language="en-US" @input="handleInput" @on-upload-img="handleUploadImg">
    <template #defToolbars>
      <NormalToolbar title="fullscreen" @onClick="handleFullClick">
        <template #trigger>
          <Maximize class='w-4 h-4 mt-1' />
        </template>
      </NormalToolbar>
    </template>
  </MdEditor>
  <Teleport to="body" v-if='isFullscreen'>
    <MdEditor v-model="text" theme="dark" :autoDetectCode="true" :editorId="`full-${editorId}`" :toolbars="toolbar"
      language="en-US" :pageFullscreen="true" class="fixed top-0 left-0 w-[100vw] h-[100vh] z-12000"
      @input="handleInput" @on-upload-img="handleUploadImg">
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
import { useToaster } from '@/components/modules/toats/index'
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
    document.querySelectorAll('[role="dialog"]').forEach(el => el.style.display = 'none');
    document.querySelector('body').style['pointer-events'] = 'auto';
  } else {
    screenfull.exit();
    document.querySelectorAll('[role="dialog"]').forEach(el => el.style.display = 'block');
    document.querySelector('body').style['pointer-events'] = 'none';
  }
};
const props = defineProps({
  editorId: String,
  modelValue: String,
  modelModifiers: Object,
  autoDetectCode: {
    type: Boolean,
    default: true
  }
})
const text = ref(props.modelValue);
const emit = defineEmits(['update:modelValue', 'isUploading'])
const handleInput = () => {
  emit('update:modelValue', text)
};

const MAX_SIZE = 20 * 1024 * 1024; // 20MB
const MAX_RETRIES = 3;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

const uploadWithRetry = async (file, retryCount = 0) => {
  try {
    const res = await uploadImage(file);
    if (!res.data?.url) {
      throw new Error('Upload response missing URL');
    }
    return res.data.url;
  } catch (error) {
    console.error(`Upload attempt ${retryCount + 1} failed:`, error);
    if (retryCount < MAX_RETRIES) {
      await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
      return uploadWithRetry(file, retryCount + 1);
    }
    throw error;
  }
};

const handleUploadImg = async (files, callback) => {
  const invalidFiles = files.filter(file => !ALLOWED_TYPES.includes(file.type));
  if (invalidFiles.length > 0) {
    useToaster.warning('Only image files allowed (jpg, png, gif, webp)');
    return;
  }

  const oversizedFiles = files.filter(file => file.size > MAX_SIZE);
  if (oversizedFiles.length > 0) {
    useToaster.warning('Image size cannot exceed 20MB');
    return;
  }
  try {
    emit('isUploading', true);
    const urls = [];
    for (let i = 0; i < files.length; i++) {
      const url = await uploadWithRetry(files[i]);
      urls.push(url);
    }
    if (urls.length === files.length) {
      callback(urls);
    } else {
      useToaster.error('Some files failed to upload');
    }
  } catch (error) {
    useToaster.error('Upload failed, please try again');
  } finally {
    emit('isUploading', false);
  }
};



const editorRef = ref(null);

config({
  editorExtensions: {
    highlight: {
      instance: highlight,
    },
    prettier: {
      prettierInstance: prettier,
      parserMarkdownInstance: 'markdown',
    },
    cropper: {
      instance: cropper,
    },
    screenfull: {
      instance: screenfull,
    },
  },

});
</script>
<style scoped>
:deep(.md-editor-toolbar-item svg.md-editor-icon) {
  @apply w-6 h-6;
}
:deep(.md-editor-menu-item.md-editor-menu-item-image:last-child) {
  @apply hidden;
}
</style>
