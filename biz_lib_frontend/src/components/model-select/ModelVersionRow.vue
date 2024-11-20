<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { ModelDetail } from '@/components/model-detail'
import vDialog from '@/components/modules/vDialog.vue'
import { modelStore } from '@/stores/modelStatus'
import {
  TableCell,
  TableRow,
} from '@/components/ui/table'

import type { Model, ModelVersion } from '@/types/model'
import { ref, watch } from 'vue'
interface Props {
  version: ModelVersion,
  model: Model
}
defineProps<Props>()
const modelStoreInstance = modelStore()
const showModelDetail = ref(false)


watch(() => modelStoreInstance.reload, (newValue: number, oldValue: number) => {
  if (newValue !== oldValue) {
    showModelDetail.value = false
  }
}, { deep: true })

const handleApply = (version: ModelVersion, model: Model) => {
  modelStoreInstance.setApplyObject(version, model)
}

const handleShowModelDetail = () => {
  showModelDetail.value = true
}


</script>
<template>
  <TableRow class=" bg-[#3D3D3D] hover:bg-[#4E4E4E] hover:cursor-pointer border-[#F9FAFB]/60 h-12"
    @click="handleShowModelDetail">
    <TableCell class="pl-10 w-[55%] max-w-[200px]">
      <div class="text-sm text-white-500 flex items-center min-w-0">
        <span class="truncate flex-1">{{ version.version }}</span>
        <div class="flex-shrink-0 ml-2">
          <svg v-if="version.public" xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17"
            fill="none">
            <path
              d="M1.33325 8.49992C1.33325 8.49992 3.33325 3.83325 7.99992 3.83325C12.6666 3.83325 14.6666 8.49992 14.6666 8.49992C14.6666 8.49992 12.6666 13.1666 7.99992 13.1666C3.33325 13.1666 1.33325 8.49992 1.33325 8.49992Z"
              stroke="#9CA3AF" stroke-linecap="round" stroke-linejoin="round" />
            <path
              d="M7.99992 10.4999C9.10449 10.4999 9.99992 9.60449 9.99992 8.49992C9.99992 7.39535 9.10449 6.49992 7.99992 6.49992C6.89535 6.49992 5.99992 7.39535 5.99992 8.49992C5.99992 9.60449 6.89535 10.4999 7.99992 10.4999Z"
              stroke="#9CA3AF" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17" fill="none">
            <path
              d="M6.58658 7.08659C6.39009 7.26968 6.23248 7.49048 6.12317 7.73582C6.01386 7.98115 5.95508 8.24598 5.95034 8.51452C5.9456 8.78307 5.995 9.04981 6.09559 9.29884C6.19618 9.54788 6.3459 9.7741 6.53582 9.96402C6.72573 10.1539 6.95196 10.3037 7.20099 10.4042C7.45003 10.5048 7.71677 10.5542 7.98531 10.5495C8.25385 10.5448 8.51869 10.486 8.76402 10.3767C9.00935 10.2674 9.23015 10.1097 9.41325 9.91325M7.15325 3.88659C7.43412 3.85159 7.71687 3.83378 7.99992 3.83325C12.6666 3.83325 14.6666 8.49992 14.6666 8.49992C14.3685 9.138 13.9947 9.73787 13.5533 10.2866M4.40659 4.90659C3.08075 5.80967 2.01983 7.05009 1.33325 8.49992C1.33325 8.49992 3.33325 13.1666 7.99992 13.1666C9.27719 13.17 10.5271 12.7967 11.5933 12.0933M1.33325 1.83325L14.6666 15.1666"
              stroke="#9CA3AF" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
      </div>
    </TableCell>
    <TableCell class="w-[15%] ">{{ version.base_model }}</TableCell>
    <TableCell class="w-[15%]">{{ version.available ? 'Available' : 'Unavailable' }}</TableCell>
    <TableCell class="w-[15%] flex justify-start">
      <Button variant="default" @click.stop="handleApply(version, model)" :disabled="!version.available"
        :class="{ 'opacity-50': !version.available }">
        Apply
      </Button>
    </TableCell>
  </TableRow>
  <vDialog v-model:open="showModelDetail" class="max-w-full h-screen px-6 overflow-hidden  pb-6 z-[8000]"
    contentClass="custom-scrollbar max-h-[100vh-120px]  overflow-y-auto w-full rounded-tl-lg rounded-tr-lg custom-shadow"
    :title="model.name">
    <ModelDetail :modelId="model.id" :version="version" />
  </vDialog>
</template>
