<script setup lang="ts">
import { Button } from '@/components/ui/button'

interface Props {
  currentPage: number
  totalPages: number
}

interface Emits {
  (e: 'change', page: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handlePrevious = () => {
  if (props.currentPage > 1) {
    emit('change', props.currentPage - 1)
  }
}

const handleNext = () => {
  if (props.currentPage < props.totalPages) {
    emit('change', props.currentPage + 1)
  }
}
</script>

<template>
  <div class="flex justify-between items-center mt-4">
    <Button variant="ghost" size="sm" :disabled="currentPage <= 1" @click="handlePrevious"
      class="text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]">
      Previous
    </Button>

    <span class="text-sm text-[#9CA3AF]">
      Page {{ currentPage }} of {{ totalPages }}
    </span>

    <Button variant="ghost" size="sm" :disabled="currentPage >= totalPages" @click="handleNext"
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