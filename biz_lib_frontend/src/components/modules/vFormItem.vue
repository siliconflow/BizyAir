<script setup lang="ts">
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import type { DateFieldRootEmits } from 'radix-vue'
import { useForwardPropsEmits } from 'radix-vue'
const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  label: String,
  description: String
})
const emits = defineEmits<DateFieldRootEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <FormField v-slot="{ componentField }" v-bind="forwarded">
    <FormItem>
      <FormLabel>{{ label }}</FormLabel>
      <FormControl>
        <!-- <Input type="text" placeholder="shadcn" v-bind="componentField" /> -->
        <slot v-bind="componentField" />
      </FormControl>
      <FormDescription>
        {{ props.description }}
      </FormDescription>
      <FormMessage />
    </FormItem>
  </FormField>
</template>
