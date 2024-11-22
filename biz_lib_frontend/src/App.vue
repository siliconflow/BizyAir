<template>
  <div class="shadcn-root flex w-full">
    <btnExample />
    <btnProfile v-if="statusStore.isLogin" />
    <btnApiKey  v-else />
    <btnModel />
    <btnNews />
    <apiKeyDialog />
  </div>
</template>
<script setup lang="ts">
import btnExample from '@/views/btnExample/index.vue'
import btnApiKey from '@/views/btnApiKey/index.vue'
import btnProfile from '@/views/btnProfile/index.vue'
import btnModel from '@/views/btnModel/index.vue'
import btnNews from '@/views/btnNews/index.vue'
import apiKeyDialog from '@/views/btnApiKey/apiKeyDialog.vue'
import { useStatusStore } from '@/stores/userStatus'

const statusStore = useStatusStore()
statusStore.loginRefresh()
statusStore.sendSocket()

</script>
<style scoped></style>
