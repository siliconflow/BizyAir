<script setup lang="ts">
import { ref } from 'vue'

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
import { ScrollArea } from '@/components/ui/scroll-area'

import vDialog from '@/components/modules/vDialog.vue'
 import  {useToaster}  from '@/components/modules/toats/index'

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

const isLoading = ref(false)

const models = ref<Model[]>([])
const getModelList = async () => {
  try {
    isLoading.value = true
    const response = await get_model_list(modelListPathParams.value, filterState.value)
    if (response && response.data) {
      modelListPathParams.value.total = response?.data?.total || 0
      models.value = response?.data?.list || []
    } else {
      modelListPathParams.value.total = 0
      models.value = []
      useToaster.warning('Unable to get model list at the moment. Please try again.')
    }
  } catch (error) {
    modelListPathParams.value.total = 0
    models.value = []
  }
  finally {
    isLoading.value = false
  }
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
  //reset Models
  models.value = []
  if (isLoading.value) return
  modelListPathParams.value.mode = String(value) as 'my' | 'my_fork' | 'publicity'
  modelListPathParams.value.current = 1
  filterState.value.keyword = ''
  filterState.value.model_types = [props.modelType || '']
  filterState.value.base_models = props.selectedBaseModels || []
  filterState.value.sort = 'Recently'
  await getModelList()
}

const emit = defineEmits(['apply'])

const handleApply = (version: ModelVersion, model: Model) => {
  emit('apply', version, model.name)
}

const handleRemove = async () => {
  await getModelList()
}

onMounted(async () => {
  await getModelList()
  showDialog.value = true
})
</script>

<template>
  <v-dialog v-model:open="showDialog" class="max-w-[70%] px-6  pb-6">
    <div class="font-['Inter']">
      <DialogTitle class="text-[#F9FAFB] mb-2 text-[18px] font-semibold leading-[18px] tracking-[-0.45px]">Select Model
      </DialogTitle>
      <DialogDescription class="text-sm text-gray-500" v-show="false" />
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
        <TabsContent value="my" v-if="modelListPathParams.mode === 'my'">
          <ModelFilterBar v-model:filter-state="filterState" :mode="modelListPathParams.mode"
            v-model:show-sort-popover="showSortPopover" :model-type="props.modelType"
            @update:filter-state="handleFilterStateChange" :selected-base-models="props.selectedBaseModels" />
          <ScrollArea class="h-[450px] rounded-md border-0">
            <ModelTable v-if="models" :models="models" :mode="modelListPathParams.mode" @apply="handleApply"
              @reload="handleRemove" />
          </ScrollArea>
          <ModelPagination :current="modelListPathParams.current" :page_size="modelListPathParams.page_size"
            :total="modelListPathParams.total" @change="handlePageChange" />
        </TabsContent>
        <TabsContent value="my_fork" v-if="modelListPathParams.mode === 'my_fork'">
          <ModelFilterBar v-model:filter-state="filterState" :mode="modelListPathParams.mode"
            v-model:show-sort-popover="showSortPopover" :model-type="props.modelType"
            @update:filter-state="handleFilterStateChange" :selected-base-models="props.selectedBaseModels" />
          <ScrollArea class="h-[450px] rounded-md border-0">
            <ModelTable v-if="models" :models="models" :mode="modelListPathParams.mode" @apply="handleApply"
              @reload="handleRemove" />
          </ScrollArea>
          <ModelPagination :current="modelListPathParams.current" :page_size="modelListPathParams.page_size"
            :total="modelListPathParams.total" @change="handlePageChange" />
        </TabsContent>
        <TabsContent value="publicity" v-if="modelListPathParams.mode === 'publicity'">
          <ModelFilterBar v-model:filter-state="filterState" :mode="modelListPathParams.mode"
            v-model:show-sort-popover="showSortPopover" :model-type="props.modelType"
            @update:filter-state="handleFilterStateChange" :selected-base-models="props.selectedBaseModels" />
          <ScrollArea class="h-[450px] rounded-md border-0">
            <ModelTable v-if="models" :models="models" :mode="modelListPathParams.mode" @apply="handleApply"
              @reload="handleRemove" />
          </ScrollArea>
          <ModelPagination :current="modelListPathParams.current" :page_size="modelListPathParams.page_size"
            :total="modelListPathParams.total" @change="handlePageChange" />
        </TabsContent>
      </Tabs>
    </div>
  </v-dialog>
</template>

<style scoped>
.custom-shadow {
  box-shadow: 0px -6px 20px 0px rgba(255, 255, 255, 0.10);
}
</style>
