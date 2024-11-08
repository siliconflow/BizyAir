<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectGroup,
  // SelectItem,
  // SelectLabel,
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
    <SelectTrigger :class="class">
      <SelectValue :placeholder="placeholder" />
    </SelectTrigger>
    <SelectContent>
      <SelectGroup>
        <slot />
      </SelectGroup>
    </SelectContent>
  </Select>
</template>
