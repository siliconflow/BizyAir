<script setup lang="ts">
import { Button } from '@/components/ui/button'

interface Props {
  current: number
  page_size: number
  total: number
}

interface Emits {
  (e: 'change', page: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handlePrevious = () => {
  if (props.current > 1) {
    emit('change', props.current - 1)
  }
}

const handleNext = () => {
  if (props.current < Math.ceil(props.total / props.page_size)) {
    emit('change', props.current + 1)
  }
}
</script>

<template>
  <div class="flex justify-between items-center mt-4" v-if="props.total > 0">
    <Button variant="ghost" size="sm" :disabled="props.current <= 1" @click="handlePrevious"
      class="text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]">
      Previous
    </Button>

    <span class="text-sm text-[#9CA3AF]">
      Page {{ props.current }} of {{ Math.ceil(props.total / props.page_size) }}
    </span>

    <Button variant="ghost" size="sm" :disabled="props.current >= props.total" @click="handleNext"
      class="text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]">
      Next
    </Button>
  </div>
</template>

<style scoped>
.button-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>