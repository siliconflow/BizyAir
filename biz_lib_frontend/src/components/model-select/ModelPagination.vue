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
import { computed } from 'vue';

const modelStoreInstance = modelStore()

interface Emits {
  (e: 'change'): void
}
const showPagination = computed(() => {
  return modelStoreInstance.modelListPathParams.total / modelStoreInstance.modelListPathParams.page_size > 1
})

const emit = defineEmits<Emits>()

const handlePageChange = (page: number) => {
  modelStoreInstance.modelListPathParams.current = page
  emit('change')
}
</script>

<template>
  <div v-if="showPagination" class="flex justify-center">
    <Pagination v-slot="{ page }" :total="modelStoreInstance.modelListPathParams.total"
      :page-size="modelStoreInstance.modelListPathParams.page_size"
      :default-page="modelStoreInstance.modelListPathParams.current" :sibling-count="1" show-edges
      @update:page="handlePageChange">
      <PaginationList v-slot="{ items }" class="flex items-center gap-1">
        <PaginationFirst class="pagination-button" />
        <PaginationPrev class="pagination-button" />

        <template v-for="(item, index) in items">
          <PaginationListItem v-if="item.type === 'page'" :key="index" :value="item.value" as-child>
            <Button class="pagination-button page-button"
              :variant="item.value === page ? 'default' : 'ghost'">
              {{ item.value }}
            </Button>
          </PaginationListItem>
          <PaginationEllipsis v-else :key="item.type" :index="index" class="pagination-button" />
        </template>

        <PaginationNext class="pagination-button" />
        <PaginationLast class="pagination-button" />
      </PaginationList>
    </Pagination>
  </div>
</template>

<style scoped>
.button-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-button {
  @apply text-[#F9FAFB] hover:text-[#F9FAFB] hover:bg-[#4E4E4E];
}

.page-button {
  @apply w-10 h-10 p-0;
}
</style>