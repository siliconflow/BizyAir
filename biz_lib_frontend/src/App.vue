<template>
  <btnExample />
  <btnProfile v-if="isLogin" />
  <btnApiKey v-else />
  <btnModel />
  <btnNews />
</template>
<script setup lang="ts">
import btnExample from '@/views/btnExample/index.vue'
import btnApiKey from '@/views/btnApiKey/index.vue'
import btnProfile from '@/views/btnProfile/index.vue'
import btnModel from '@/views/btnModel/index.vue'
import btnNews from '@/views/btnNews/index.vue'
import { getUserInfo } from './api/user'
import { ref } from 'vue'
const isLogin = ref(false)

getUserInfo().then(info => {
  sessionStorage.setItem('userInfo', JSON.stringify(info.data))
  isLogin.value = true
}).catch(() => {
  isLogin.value = false
})
</script>
<style scoped></style>
