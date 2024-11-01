<template>
  <btnMenu :show_cases="show_cases" buttonText="Examples" icon="book-open" :isJson="true">
    <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
      <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 16.008V7.99a1.98 1.98 0 0 0-1-1.717l-7-4.008a2.02 2.02 0 0 0-2 0L4 6.273c-.619.355-1 1.01-1 1.718v8.018c0 .709.381 1.363 1 1.717l7 4.008a2.02 2.02 0 0 0 2 0l7-4.008c.619-.355 1-1.01 1-1.718M12 22V12m0 0l8.73-5.04m-17.46 0L12 12" />
    </svg>
  </btnMenu>
</template>
<script setup lang="ts">
import btnMenu from '@/components/modules/btnMenu.vue';
import { ref } from 'vue';
const modelList = () => {
  console.log(123)
}
const uploadWithInputPage = () => {
  console.log(123)
}
const show_cases = ref({
  "Remote Folders": modelList,
  "Upload": uploadWithInputPage,
})

</script>
<style scoped></style>
