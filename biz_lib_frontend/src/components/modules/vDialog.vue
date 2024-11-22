<script setup lang="ts">
import {
  Dialog,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DialogClose,
  DialogContent,
  DialogOverlay,
  DialogPortal,
  useForwardPropsEmits,
} from 'radix-vue'
import { defineProps, defineEmits, onMounted, onUnmounted, computed } from 'vue'
import { cn } from '@/lib/utils'
import { X } from 'lucide-vue-next'

const props = defineProps({
  open: Boolean,
  showClose: {
    type: Boolean,
    default: true,
  },
  class: {
    type: [String, Object, Array] as any,
    default: null,
  },
  contentClass: {
    type: [String, Object, Array] as any,
    default: null,
  },
  layoutClass: {
    type: [String, Object, Array] as any,
    default: null,
  },
})

const emit = defineEmits(['update:open', 'onClose'])

function closeDialog() {
  emit('update:open', false)
  emit('onClose')
}

function keyCloseDialog(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    closeDialog()
  }
}

const delegatedProps = computed(() => {
  const { ...delegated } = props

  return delegated
})

const forwarded = useForwardPropsEmits(delegatedProps, emit)

onMounted(() => {
  document.addEventListener('keydown', keyCloseDialog)
})

onUnmounted(() => {
  document.removeEventListener('keydown', keyCloseDialog)
})
</script>

<template>
  <Dialog :open="open" @close="closeDialog">
    <DialogPortal>
      <DialogOverlay
        :class="cn(
          'fixed shadcn-root inset-0 z-50 bg-black/80  data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          props.layoutClass
        )" />
      <DialogContent v-bind="forwarded" @interact-outside="(event: any) => {
        const target = event.target as HTMLElement;
        if (target?.closest('[data-sonner-toaster]')) return event.preventDefault()
      }" :class="cn(
        'shadcn-root max-w-[900px] bg-[#222] fixed left-1/2 top-1/2 z-50 grid w-full -translate-x-1/2 -translate-y-1/2 gap-4 border p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg',
        props.class)">
        <DialogHeader>
          <DialogTitle>
            <slot name="title" />
          </DialogTitle>
          <DialogDescription>
            <slot name="description" />
          </DialogDescription>
        </DialogHeader>
        <div :class="props.contentClass">
          <slot />
        </div>
        <DialogFooter>
          <slot name="foot" />
        </DialogFooter>
        <DialogClose v-if="showClose"
          class="absolute bg-transparent right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
          <X class="w-4 h-4" @click="closeDialog" />
          <span class="sr-only">Close</span>
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </Dialog>
</template>
