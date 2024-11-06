<template>
  <btnExample />
  <btnProfile v-if="!statusStore.isLogin" />
  <btnApiKey v-else />
  <btnModel />
  <btnNews />
  <!-- <Button @click="aaaaaa">aaaa</Button> -->
  <!-- <Toaster class="right-2 top-2 sticky" position="top-right" /> -->
</template>
<script setup lang="ts">
import btnExample from '@/views/btnExample/index.vue'
import btnApiKey from '@/views/btnApiKey/index.vue'
import btnProfile from '@/views/btnProfile/index.vue'
import btnModel from '@/views/btnModel/index.vue'
import btnNews from '@/views/btnNews/index.vue'
// import { Toaster } from '@/components/ui/sonner'
// import useClipboard from 'vue-clipboard3'
import { useStatusStore} from '@/stores/userStatus'

const statusStore = useStatusStore()
statusStore.loginRefresh()
statusStore.sendSocket()
// const { toClipboard } = useClipboard()
// const aaaaaa = () => {
//   toClipboard('aa111aa')
// }

</script>
<style scoped></style>
