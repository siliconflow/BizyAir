<script setup lang="ts">
import { defineProps, defineEmits, onMounted, onUnmounted } from 'vue'
import { cn } from '@/lib/utils';
import { X } from 'lucide-vue-next'
const props = defineProps({
  showClose: {
    type: Boolean,
    default: true,
  },
  open: Boolean,
  class: {
    type: [String, Object, Array] as any,
    default: null,
  },
  layoutClass: {
    type: [String, Object, Array] as any,
    default: null,
  },
})
const emit = defineEmits(['update:open', 'onClose'])
const close = () => {
  emit('update:open', false)
  emit('onClose')
}
function keyCloseDialog(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    close()
  }
}
onMounted(() => {
  document.addEventListener('keydown', keyCloseDialog)
})

onUnmounted(() => {
  document.removeEventListener('keydown', keyCloseDialog)
})
</script>
<template>
  <Teleport to="body">
    <div :class="cn('fixed w-[100vw] h-[100vh] bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0', props.layoutClass)" v-if="open">
      <div :class="cn('px-0 overflow-hidden pb-0 max-w-[900px] bg-[#222] fixed left-1/2 top-1/2 grid w-full -translate-x-1/2 -translate-y-1/2 gap-4 border p-6 shadow-lg sm:rounded-lg', props.class)">
        <X class="absolute right-2 top-2 cursor-pointer" @click="close" v-if="showClose" />
        <div v-if="$slots.title" class="font-bold">
          <slot name="title" />
        </div>

        <slot />

        <div v-if="$slots.foot" class="flex justify-end gap-2">
          <slot name="foot" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
