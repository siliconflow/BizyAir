<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { cn } from '@/lib/utils';
const props = defineProps({
  content: String,
  z: String,
  class: [String, Object, Array] as any
})
const emit = defineEmits(['update:open'])
</script>
<template>
    <div :class="cn('w-[100vw] h-[100vh] fixed inset-0 z-50 bg-black/80', props.z)">
      <div :class="cn('flex p-10 overflow-hidden max-w-[500px] bg-[#222] fixed left-1/2 top-1/2 w-full -translate-x-1/2 -translate-y-1/2 gap-2 border shadow-lg sm:rounded-lg', props.class)">
        <p>
        {{ props.content }}
        </p>
        <div class="flex justify-center space-x-1">
          <span class="w-1 h-1 mt-3.5 bg-slate-300 rounded-full animate-pulse"></span>
          <span class="w-1 h-1 mt-3.5 bg-slate-300 rounded-full animate-[pulse_1.2s_ease-in-out_0.2s_infinite]"></span>
          <span class="w-1 h-1 mt-3.5 bg-slate-300 rounded-full animate-[pulse_1.2s_ease-in-out_0.4s_infinite]"></span>
          <span class="w-1 h-1 mt-3.5 bg-slate-300 rounded-full animate-[pulse_1.2s_ease-in-out_0.6s_infinite]"></span>
          <span class="w-1 h-1 mt-3.5 bg-slate-300 rounded-full animate-[pulse_1.2s_ease-in-out_0.8s_infinite]"></span>
        </div>
      </div>
    </div>
</template>
<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}
</style>
