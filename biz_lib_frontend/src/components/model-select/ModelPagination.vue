<script setup lang="ts">
import {
  Button,
} from '@/components/ui/button'

import {
  Pagination,
  PaginationEllipsis,
  PaginationFirst,
  PaginationLast,
  PaginationList,
  PaginationListItem,
  PaginationNext,
  PaginationPrev,
} from '@/components/ui/pagination'

import { modelStore } from '@/stores/modelStatus'

const modelStoreInstance = modelStore()

interface Emits {
  (e: 'change'): void
}

const emit = defineEmits<Emits>()

const handlePageChange = (page: number) => {
  modelStoreInstance.modelListPathParams.current = page
  emit('change') // 通知父组件更新
}
</script>

<template>
  <div v-if="modelStoreInstance.modelListPathParams.total / modelStoreInstance.modelListPathParams.page_size > 1" class="flex justify-center">
    <Pagination v-slot="{ page }" :total="modelStoreInstance.modelListPathParams.total"
      :page-size="modelStoreInstance.modelListPathParams.page_size"
      :default-page="modelStoreInstance.modelListPathParams.current" :sibling-count="1" show-edges
      @update:page="handlePageChange">
      <PaginationList v-slot="{ items }" class="flex items-center gap-1">
        <PaginationFirst class="text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]" />
        <PaginationPrev class="text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]" />

        <template v-for="(item, index) in items">
          <PaginationListItem v-if="item.type === 'page'" :key="index" :value="item.value" as-child>
            <Button class="w-10 h-10 p-0 text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]"
              :variant="item.value === page ? 'default' : 'ghost'">
              {{ item.value }}
            </Button>
          </PaginationListItem>
          <PaginationEllipsis v-else :key="item.type" :index="index" class="text-[#9CA3AF]" />
        </template>

        <PaginationNext class="text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]" />
        <PaginationLast class="text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E]" />
      </PaginationList>
    </Pagination>
  </div>
</template>

<style scoped>
.button-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>