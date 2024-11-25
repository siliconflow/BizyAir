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

import { base_model_types, get_model_list, model_types } from '@/api/model'
import { onMounted } from 'vue'
import { useToaster } from '@/components/modules/toats/index'
import vDialog from '@/components/modules/vDialog.vue'
import { modelStore } from '@/stores/modelStatus'
import type { ModeType } from '@/types/model'

const modelStoreInstance = modelStore()
interface Props {
  modelType?: string[]
  selectedBaseModels?: string[]
}
const props = defineProps<Props>()
const modes = ['my', 'my_fork', 'publicity'] as const

const tabLabels: Record<ModeType, string> = {
  my: 'My Models',
  my_fork: 'My Forks',
  publicity: 'Community Models'
}


const getModelList = async () => {
  modelStoreInstance.setIsLoading(true)
  await get_model_list(modelStoreInstance.modelListPathParams, modelStoreInstance.filterState)
    .then(response => {
      if (response && response.data) {
        modelStoreInstance.modelListPathParams.total = response?.data?.total || 0
        modelStoreInstance.models = response?.data?.list || []
      } else {
        modelStoreInstance.modelListPathParams.total = 0
        modelStoreInstance.models = []
      }
    })
    .catch(error => {
      useToaster.error(`Failed to fetch model list. ${error}`)
      modelStoreInstance.modelListPathParams.total = 0
      modelStoreInstance.models = []
    })
    .finally(async () => {
      modelStoreInstance.setIsLoading(false)
    })
}

const showSortPopover = ref(false)
const showDialog = ref(false)

const handleTabChange = async (value: string | number) => {
  modelStoreInstance.models = []
  modelStoreInstance.mode = String(value) as 'my' | 'my_fork' | 'publicity'

  modelStoreInstance.modelListPathParams.mode = modelStoreInstance.mode
  modelStoreInstance.modelListPathParams.current = 1

  if (modelStoreInstance.mode !== 'publicity') {
    modelStoreInstance.filterState.sort = 'Recently'
  }

  await getModelList()
}


const getFilterData = () => {
  return model_types()
    .then(modelTypesResponse => {
      modelStoreInstance.setModelTypes(modelTypesResponse?.data ? (modelTypesResponse.data as CommonModelType[]) : [])
      return base_model_types()
    })
    .then(baseModelResponse => {
      modelStoreInstance.setBaseModelTypes(baseModelResponse?.data ? (baseModelResponse.data as CommonModelType[]) : [])
    })
    .catch(error => {
      useToaster.error(`Failed to fetch base model types${error}`)
      modelStoreInstance.setModelTypes([])
      modelStoreInstance.setBaseModelTypes([])
    })
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

watch(() => modelStoreInstance.reload, async (newVal: number, oldVal: number) => {
  if (newVal !== oldVal) {
    await getModelList()
  }
}, { deep: true })

watch(() => modelStoreInstance.reloadModelSelectList, async (newVal: boolean, oldVal: boolean) => {
  if (newVal !== oldVal) {
    await getModelList()
  }
}, { deep: true })

watch(() => modelStoreInstance.modelListPathParams.current, async (newVal: number, oldVal: number) => {

  if (newVal !== oldVal && showDialog.value) {
    await getModelList()
  }
})


onMounted(async () => {
  if (props.modelType) {
    modelStoreInstance.selectedModelTypes = props.modelType
    modelStoreInstance.filterState.model_types = props.modelType
  }
  if (props.selectedBaseModels) {
    modelStoreInstance.selectedBaseModels = props.selectedBaseModels
    modelStoreInstance.filterState.base_models = props.selectedBaseModels
  }
  await getFilterData()
  showDialog.value = true
})

watch(() => showDialog.value, async (newVal: boolean) => {
  if (newVal) {
    if (props.modelType) {
      modelStoreInstance.selectedModelTypes = props.modelType
      modelStoreInstance.filterState.model_types = props.modelType
    }
    if (props.selectedBaseModels) {
      modelStoreInstance.selectedBaseModels = props.selectedBaseModels
      modelStoreInstance.filterState.base_models = props.selectedBaseModels
    }
    await getModelList()
  } else {
    modelStoreInstance.resetModelListPathParams()
  }
})

const handleClose = () => {
  showDialog.value = false
}
</script>

<template>
  <v-dialog v-model:open="showDialog" class=" max-w-[70%]  px-6 pb-6 overflow-hidden" @onClose="handleClose"
    contentClass="custom-scrollbar max-h-[80vh] overflow-y-auto w-full rounded-tl-lg rounded-tr-lg custom-shadow">
    <template #title>
      <span class="text-[#F9FAFB] mb-4 text-[18px] font-semibold leading-[18px] tracking-[-0.45px]">
        Select Model
      </span>
    </template>

    <div class="font-['Inter'] flex flex-col ">
      <Tabs :defaultValue="modelStoreInstance.mode" class="h-full flex flex-col" @update:model-value="handleTabChange">
        <TabsList class="grid w-full grid-cols-3 h-12 bg-[#4E4E4E] text-white text-sm shrink-0">
          <TabsTrigger v-for="mode in modes" :key="mode" :value="mode"
            class="text-sm  data-[state=active]:bg-[#9CA3AF] bg-[#4E4E4E]  h-10 px-3 py-2 focus:outline-none focus-visible:outline-none">
            {{ tabLabels[mode] }}
          </TabsTrigger>
        </TabsList>

        <template v-for="mode in modes" :key="mode">
          <TabsContent v-if="modelStoreInstance.mode === mode" :value="mode"
            class="flex-1 flex flex-col overflow-hidden ">
            <div class="flex flex-col min-h-[650px] ">
              <div class="flex-1 relative">
                <ModelFilterBar v-model:show-sort-popover="showSortPopover" @fetchData="getModelList"
                  class="shrink-0" />
                <div class="h-full">
                  <ModelTable />
                </div>
              </div>
              <div class="h-4"></div>
            </div>
          </TabsContent>
        </template>
      </Tabs>
    </div>
  </v-dialog>
</template>
