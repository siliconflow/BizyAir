<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { cn } from '@/lib/utils';
import { X } from 'lucide-vue-next'
const props = defineProps({
  open: Boolean,
  class: {
    type: [String, Object, Array] as any,
    default: null,
  },
})
const emit = defineEmits(['update:open'])
const close = () => {
  emit('update:open', false)
}
</script>
<template>
  <Teleport to="body">
    <div class="shadcn-root">
      <div class="w-[100vw] h-[100vh] fixed inset-0 z-8000 bg-black/80 " v-if="open">
        <div :class="cn('fixed z-50 bg-background p-6 shadow-lg h-full border-r w-auto min-w-[560px]', props.class)">
          <X class="absolute right-2 top-2 cursor-pointer" @click="close" />
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>
