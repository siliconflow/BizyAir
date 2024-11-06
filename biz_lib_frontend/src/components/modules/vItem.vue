<script setup lang="ts">
defineProps({
  label: String,
  required: Boolean,
})
</script>

<template>
  <div>
    <p class="text-sm mt-3">{{ label }}<span v-if="required">*</span></p>
    <div class="mt-2">
      <slot />
    </div>
  </div>
</template>
