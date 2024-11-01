<template>
  <btnMenu :show_cases="show_cases" buttonText="Examples" icon="book-open" :isJson="true">
    <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
      <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.603c1.667-1.271 5.5-2.86 9 0V19c-3.5-2.86-7.333-1.271-9 0m0-12.397c-1.667-1.271-5.5-2.86-9 0V19c3.5-2.86 7.333-1.271 9 0m0-12.397V19" />
    </svg>
  </btnMenu>
</template>
<script setup lang="ts">
import btnMenu from '@/components/modules/btnMenu.vue';
import { ref } from 'vue';
const show_cases = ref({})
fetch("api/bizyair/showcases", { method: "GET" }).then(response => response.json()).then(data => {
    show_cases.value = data
});
</script>
<style scoped></style>
