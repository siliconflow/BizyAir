<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Markdown } from '@/components/markdown'

import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent
} from '@/components/ui/tabs'
import type { Model, FilterState, ModelListPathParams, ModelVersion } from '@/types/model'
import ModelFilterBar from './ModelFilterBar.vue'
import ModelTable from './ModelTable.vue'
import ModelPagination from './ModelPagination.vue'
import { get_model_list } from '@/api/model'
import { onMounted } from 'vue'

import vDialog from '@/components/modules/vDialog.vue'

interface Props {
  modelType?: string
  selectedBaseModels?: string[]
}

const props = defineProps<Props>()

const modelListPathParams = ref<ModelListPathParams>({
  mode: 'my',
  current: 1,
  page_size: 5,
  total: 0
})

const filterState = ref<FilterState>({
  keyword: '',
  model_types: [props.modelType || ''],
  base_models: props.selectedBaseModels || [],
  sort: 'Recently'
})
const models = ref<Model[]>([])
const getModelList = async () => {
  const { data } = await get_model_list(modelListPathParams.value, filterState.value)
  modelListPathParams.value.total = data?.total || 0
  models.value = data?.list || []
}

const showSortPopover = ref(false)
const showDialog = ref(false)
const handlePageChange = async (page: number) => {
  modelListPathParams.value.current = page
  await getModelList()
}

const handleFilterStateChange = async (value: FilterState) => {
  filterState.value = value
  await getModelList()
}

const handleTabChange = async (value: string | number) => {
  modelListPathParams.value.mode = String(value) as 'my' | 'my_fork' | 'publicity'
  modelListPathParams.value.current = 1
  filterState.value.keyword = ''
  filterState.value.model_types = [props.modelType || '']
  filterState.value.base_models = props.selectedBaseModels || []
  filterState.value.sort = 'Recently'
  await getModelList()
}



const handleApply = (version: ModelVersion) => {
  //TODO: apply model to bizyair node & close dialog
  //emit apply event
  console.log('version', version)
}

onMounted(async () => {
  await getModelList()
  showDialog.value = true
})


</script>

<template>
  <v-dialog v-model:open="showDialog">
    <div class="p-2 font-['Inter']">
      <DialogTitle class="text-xl font-bold">Select Model</DialogTitle>
      <DialogDescription class="text-sm text-gray-500" />
      <div class="flex items-center justify-end mb-4">
        <Button variant="ghost" class="h-8 w-8 p-0">
          <span class="sr-only">Close</span>
        </Button>
      </div>
      <Tabs :defaultValue="modelListPathParams.mode" class="mb-4" @update:model-value="handleTabChange">
        <TabsList class="grid w-full grid-cols-3 h-12 bg-[#4E4E4E] text-sm">
          <TabsTrigger value="my"
            class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">
            My Models
          </TabsTrigger>
          <TabsTrigger value="my_fork"
            class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">
            My Forks
          </TabsTrigger>
          <TabsTrigger value="publicity"
            class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">
            Community Models
          </TabsTrigger>
        </TabsList>
        <TabsContent value="my">
          <ModelFilterBar v-model:filter-state="filterState" v-model:show-sort-popover="showSortPopover"
            :model-type="props.modelType" @update:filter-state="handleFilterStateChange"
            :selected-base-models="props.selectedBaseModels" />
          <ScrollArea class="h-[500px] rounded-md border-0">
            <ModelTable :models="models" @apply="handleApply" />
          </ScrollArea>
          <ModelPagination :current="modelListPathParams.current" :page_size="modelListPathParams.page_size"
            :total="modelListPathParams.total" @change="handlePageChange" />
        </TabsContent>
        <TabsContent value="my_fork">
          <ModelFilterBar v-model:filter-state="filterState" v-model:show-sort-popover="showSortPopover"
            :model-type="props.modelType" @update:filter-state="handleFilterStateChange"
            :selected-base-models="props.selectedBaseModels" />
          <ScrollArea class="h-[500px] rounded-md border-0">
            <ModelTable :models="models" @apply="handleApply" />
          </ScrollArea>
          <ModelPagination :current="modelListPathParams.current" :page_size="modelListPathParams.page_size"
            :total="modelListPathParams.total" @change="handlePageChange" />
        </TabsContent>
        <TabsContent value="publicity">
          <ModelFilterBar v-model:filter-state="filterState" v-model:show-sort-popover="showSortPopover"
            :model-type="props.modelType" @update:filter-state="handleFilterStateChange"
            :selected-base-models="props.selectedBaseModels" />
          <ScrollArea class="h-[400px] rounded-md border-0">
            <ModelTable :models="models" @apply="handleApply" />
          </ScrollArea>
          <ModelPagination :current="modelListPathParams.current" :page_size="modelListPathParams.page_size"
            :total="modelListPathParams.total" @change="handlePageChange" />
        </TabsContent>
      </Tabs>
    </div>
  </v-dialog>
</template>