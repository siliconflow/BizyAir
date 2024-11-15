<script setup lang="ts">
import { ref, watch } from 'vue'

import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent
} from '@/components/ui/tabs'
import type { Model, ModelVersion, CommonModelType } from '@/types/model'
import ModelFilterBar from './ModelFilterBar.vue'
import ModelTable from './ModelTable.vue'
import ModelPagination from './ModelPagination.vue'
import { base_model_types, get_model_list, model_types } from '@/api/model'
import { onMounted } from 'vue'

import vDialog from '@/components/modules/vDialog.vue'
import { modelStore } from '@/stores/modelStatus'

const modelStoreInstance = modelStore()
interface Props {
  modelType?: string[]
  selectedBaseModels?: string[]
}

const props = defineProps<Props>()

const isLoading = ref(false)

const models = ref<Model[]>([])
const getModelList = async () => {
  console.log('[modelStoreInstance.filterState]', modelStoreInstance.filterState)
  try {
    isLoading.value = true
    const response = await get_model_list(modelStoreInstance.modelListPathParams, modelStoreInstance.filterState)
    if (response && response.data) {
      modelStoreInstance.modelListPathParams.total = response?.data?.total || 0
      models.value = response?.data?.list || []
    } else {
      modelStoreInstance.modelListPathParams.total = 0
      models.value = []
    }
  } catch (error) {
    modelStoreInstance.modelListPathParams.total = 0
    models.value = []
  }
  finally {
    isLoading.value = false
  }
}

const showSortPopover = ref(false)
const showDialog = ref(false)


const handleTabChange = async (value: string | number) => {
  models.value = []
  modelStoreInstance.mode = String(value) as 'my' | 'my_fork' | 'publicity'
  if (isLoading.value) return
  modelStoreInstance.modelListPathParams.mode = modelStoreInstance.mode
  modelStoreInstance.modelListPathParams.current = 1

  if (modelStoreInstance.mode !== 'publicity') {
    modelStoreInstance.filterState.sort = 'Recently'
  }

  await getModelList()
}


const getFilterData = async () => {
  try {
    const modelTypesResponse = await model_types()
    modelStoreInstance.setModelTypes(modelTypesResponse?.data ? (modelTypesResponse.data as CommonModelType[]) : [])

    const baseModelResponse = await base_model_types()
    console.log('[baseModelResponse]', baseModelResponse)
    modelStoreInstance.setBaseModelTypes(baseModelResponse?.data ? (baseModelResponse.data as CommonModelType[]) : [])
  } catch (error) {
    modelStoreInstance.setModelTypes([])
    modelStoreInstance.setBaseModelTypes([])
  }
}

const emit = defineEmits(['apply'])

watch(() => modelStoreInstance.applyObject, (newVal: { version: ModelVersion, model: Model }) => {
  if (newVal.version && newVal.model) {
    emit('apply', newVal.version, newVal.model.name)
  }
}, { deep: true, immediate: true })

watch(() => modelStoreInstance.closeModelSelectDialog, (newVal: boolean, oldVal: boolean) => {
  if (newVal !== oldVal) {
    showDialog.value = false
  }
}, { deep: true })

watch(() => modelStoreInstance.reload, (newVal: number, oldVal: number) => {
  if (newVal !== oldVal) {
    getModelList()
  }
}, { deep: true })

watch(() => modelStoreInstance.reloadModelSelectList, (newVal: boolean, oldVal: boolean) => {
  if (newVal !== oldVal) {
    getModelList()
  }
}, { deep: true })

onMounted(async () => {
  if (props.modelType) {
    modelStoreInstance.selectedModelTypes = props.modelType
    modelStoreInstance.filterState.model_types = props.modelType
  }
  if (props.selectedBaseModels) {
    modelStoreInstance.selectedBaseModels = props.selectedBaseModels
    modelStoreInstance.filterState.base_models = props.selectedBaseModels
  }

  console.log('[modelStoreInstance.filterState]', modelStoreInstance.filterState)
  await getFilterData()
  await getModelList()
  showDialog.value = true
})

</script>

<template>
  <v-dialog v-model:open="showDialog" class="max-w-[70%] px-6  pb-6">
    <template #title><span
        class="text-[#F9FAFB] mb-4 text-[18px] font-semibold leading-[18px] tracking-[-0.45px]">Select
        Model</span></template>
    <div class="font-['Inter']">
      <Tabs :defaultValue="modelStoreInstance.mode" class="mb-4" @update:model-value="handleTabChange">
        <TabsList class="grid w-full grid-cols-3 h-12 bg-[#4E4E4E] text-sm">
          <TabsTrigger value="my"
            class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2 focus:outline-none focus-visible:outline-none">
            My Models
          </TabsTrigger>
          <TabsTrigger value="my_fork"
            class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2 focus:outline-none focus-visible:outline-none">
            My Forks
          </TabsTrigger>
          <TabsTrigger value="publicity"
            class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2 focus:outline-none focus-visible:outline-none">
            Community Models
          </TabsTrigger>
        </TabsList>
        <TabsContent value="my" v-if="modelStoreInstance.mode === 'my'">
          <ModelFilterBar v-model:show-sort-popover="showSortPopover" @fetchData="getModelList" />
          <div class="min-h-[450px]">
            <ModelTable v-if="models.length > 0" :models="models" />
          </div>
          <ModelPagination @change="getModelList" />
        </TabsContent>
        <TabsContent value="my_fork" v-if="modelStoreInstance.mode === 'my_fork'">
          <ModelFilterBar v-model:show-sort-popover="showSortPopover" @fetchData="getModelList" />
          <div class="min-h-[450px]">
            <ModelTable v-if="models.length > 0" :models="models" />
          </div>
          <ModelPagination @change="getModelList" />
        </TabsContent>
        <TabsContent value="publicity" v-if="modelStoreInstance.mode === 'publicity'">
          <ModelFilterBar v-model:show-sort-popover="showSortPopover" @fetchData="getModelList" />
          <div class="min-h-[450px]">
            <ModelTable v-if="models.length > 0" :models="models" />
          </div>
          <ModelPagination @change="getModelList" />
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
