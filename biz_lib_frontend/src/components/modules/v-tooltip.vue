<template>
  <TooltipProvider class="shadcn-root">
    <Tooltip>
      <TooltipTrigger as-child>
        <span>
          <slot />
        </span>
      </TooltipTrigger>
      <TooltipContent>
        <span>{{ tips }}</span>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
</template>
<script setup lang="ts">
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
defineProps({
  tips: String
})
</script>
<style scoped></style>
