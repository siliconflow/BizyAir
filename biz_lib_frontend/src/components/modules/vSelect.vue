<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { PropType } from 'vue'
import type { SelectRootEmits } from 'radix-vue'
import { useForwardPropsEmits } from 'radix-vue'

const props = defineProps({
  modelValue: String,
  placeholder: String,
  class: [String, Object, Array],
  'onUpdate:modelValue': Function as PropType<(value: string) => void>,
})
const emits = defineEmits<SelectRootEmits>()

const forwarded = useForwardPropsEmits(props, emits)

</script>

<template>
  <Select v-bind="forwarded">
    <div class="shadcn-root">
      <SelectTrigger :class="class">
        <SelectValue :placeholder="placeholder" />
      </SelectTrigger>
    </div>
    <SelectContent class="z-9000 shadcn-root">
      <SelectGroup>
        <slot />
      </SelectGroup>
    </SelectContent>
  </Select>
</template>
