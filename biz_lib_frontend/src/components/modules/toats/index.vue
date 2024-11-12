<script setup lang="ts">
import { defineProps, defineEmits, ref, onMounted } from 'vue'
import { X, CircleX, Check, TriangleAlert } from 'lucide-vue-next'

const iTimer = ref<ReturnType<typeof setTimeout>>()
defineProps({
  message: String,
  type: {
    type: String,
    default: 'info',
    enum: ['success', 'error', 'warning', 'info'],
  },
  z: String,
})
const emit = defineEmits(['close'])
const close = () => {
  emit('close')
}

function stopTimeout() {
  clearTimeout(iTimer.value)
}
function startTimeout() {
  iTimer.value = setTimeout(() => {
    close()
  }, 5000)
}
onMounted(() => {
  startTimeout()
})
</script>

<template>
  <div :class="[
    `mt-2 relative flex w-96 min-h-14 z-50 rounded-md p-5 ${z}`,
    {'bg-green-500/30 border-green-500/30 text-green-500': type === 'info'},
    {'bg-green-500/30 border-green-500/30 text-green-500': type === 'success'},
    {'bg-red-500/30 border-red-500/30 text-red-500': type === 'error'},
    {'bg-yellow-500/30 border-yellow-500/30 text-yellow-500': type === 'warning'},
    ]"
    @mouseover="stopTimeout"
    @mouseout="startTimeout">
    <Check class="w-6 h-6 mr-2" v-if="type === 'success'" />
    <CircleX class="w-6 h-6 mr-2" v-if="type === 'error'" />
    <TriangleAlert class="w-6 h-6 mr-2" v-if="type === 'warning'" />
    <span class="flex-1">
      {{ message }}
    </span>
    <X class="absolute right-2 top-2 cursor-pointer" @click="close" />
  </div>
</template>
