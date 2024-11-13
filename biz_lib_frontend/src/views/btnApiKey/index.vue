<template>
  <div @click="statusStore.handleApiKeyDialog(true)" class="flex items-center hover:bg-[#4A238E] cursor-pointer relative px-3">
    <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
      <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
        d="m15.362 9.065l1.32 1.32c.995.995 1.345-.84 2.734-1.07c.466-.078.877-.236 1.053-.752c.156-.456-.021-.885-.574-1.438L18.5 5.731M7.5 21a4.5 4.5 0 1 0 0-9a4.5 4.5 0 0 0 0 9m3.5-8L21 3" />
    </svg>
    <span class="block leading h-full leading-8 text-sm">API Key</span>
  </div>
</template>
<script setup lang="ts">
import { useStatusStore} from '@/stores/userStatus'
const statusStore = useStatusStore()
</script>
<style scoped></style>
