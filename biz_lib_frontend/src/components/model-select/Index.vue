<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogDescription
} from '@/components/ui/dialog'
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent
} from '@/components/ui/tabs'
import type { Model, FilterState } from '@/types/model'
import ModelFilterBar from './ModelFilterBar.vue'
import ModelTable from './ModelTable.vue'
import ModelPagination from './ModelPagination.vue'

const filterState = ref<FilterState>({
  mode: 'my',
  keyword: '',
  modelTypes: ['checkpoint'],
  baseModels: ['SDXL 1.0'],
  sort: 'recently'
})

const models = ref<Model[]>([
  {
    name: 'Model A',
    version: 'V1.0',
    baseModel: 'SDXL 1.0',
    status: 'Available',
    isPublic: true,
    isCheckpoint: true,
    versions: [{
      version: 'V1.0',
      baseModel: 'SDXL 1.0',
      status: 'Available'
    }, {
      version: 'V1.1',
      baseModel: 'SDXL 1.1',
      status: 'Unavailable',
    }]
  },
  // ... 其他模型数据
])

const showSortPopover = ref(true)
const currentPage = ref(1)
const totalPages = ref(5)
const showDialog = ref(true)




const handlePageChange = (page: number) => {
  currentPage.value = page
  // TODO: 加载对应页面的数据
}
</script>

<template>
  <Dialog :open="showDialog" @update:open="showDialog = $event">
    <DialogContent class="max-w-[900px] bg-[#222]">
      <div class="p-2 font-['Inter']">
        <DialogTitle class="text-xl font-bold">Select Model</DialogTitle>
        <DialogDescription class="text-sm text-gray-500" />

        <div class="flex items-center justify-end mb-4">
          <Button variant="ghost" class="h-8 w-8 p-0">
            <span class="sr-only">Close</span>
          </Button>
        </div>

        <Tabs defaultValue="my-posts" class="mb-4">
          <TabsList class="grid w-full grid-cols-3 h-12 bg-[#4E4E4E] text-sm">
            <TabsTrigger value="my-posts"
              class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">
              My Models
            </TabsTrigger>
            <TabsTrigger value="my-forks"
              class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">
              My Forks
            </TabsTrigger>
            <TabsTrigger value="community"
              class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">
              Community Models
            </TabsTrigger>
          </TabsList>

          <TabsContent value="my-posts">
            <ModelFilterBar v-model:filter-state="filterState" v-model:show-sort-popover="showSortPopover" />

            <ScrollArea class="h-[500px] rounded-md border-0">
              <ModelTable :models="models" />
            </ScrollArea>

            <ModelPagination :current-page="currentPage" :total-pages="totalPages" @change="handlePageChange" />
          </TabsContent>

          <TabsContent value="my-forks">
            <!-- My Forks content -->
          </TabsContent>

          <TabsContent value="community">
            <!-- Community content -->
          </TabsContent>
        </Tabs>
      </div>
    </DialogContent>
  </Dialog>
</template>