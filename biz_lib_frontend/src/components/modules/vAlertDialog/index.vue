<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
const showAlert = ref(true)
defineProps({
  cancel: {
    type: String,
    default: 'Cancel',
  },
  continue: {
    type: String,
    default: 'Continue',
  },
  title: {
    type: String,
    default: 'Are you absolutely sure?',
  },
  desc: String,
  z: String,
})

const emit = defineEmits(['continueClick', 'cancelClick'])
const continueBtn = () => {
  emit('continueClick')
}
const cancelBtn = () => {
  emit('cancelClick')
}
</script>

<template>
  <AlertDialog v-model:open="showAlert">
    <AlertDialogContent :class="z">
      <AlertDialogHeader>
        <AlertDialogTitle>{{ title }}</AlertDialogTitle>
        <AlertDialogDescription>{{ desc }}</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="cancelBtn">{{ cancel }}</AlertDialogCancel>
        <AlertDialogAction @click="continueBtn">{{ continue }}</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
