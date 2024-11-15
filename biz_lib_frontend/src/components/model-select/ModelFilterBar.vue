<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { model_types, base_model_types } from '@/api/model'
import { onMounted, ref } from 'vue'
import type { FilterState, CommonModelType } from '@/types/model'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import {
  Command,
  CommandGroup,
  CommandItem,
  CommandList,
  CommandSeparator
} from '@/components/ui/command'

const modelTypes = ref<CommonModelType[]>([])
const baseModelTypes = ref<CommonModelType[]>([])
const selectedBaseModels = ref<string[]>([])
const isLoading = ref(false)
interface Props {
  filterState: FilterState
  showSortPopover: boolean
  modelType?: string
  selectedBaseModels?: string[]
  mode: string
}

interface Emits {
  (e: 'update:filterState', value: FilterState): void
  (e: 'update:showSortPopover', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const getFilterData = async () => {
  try {
    isLoading.value = true
    const modelTypesResponse = await model_types()
    modelTypes.value = modelTypesResponse?.data ? (modelTypesResponse.data as CommonModelType[]) : []

    const baseModelResponse = await base_model_types()
    baseModelTypes.value = baseModelResponse?.data ? (baseModelResponse.data as CommonModelType[]) : []
  } catch (error) {
    modelTypes.value = []
    baseModelTypes.value = []

  } finally {
    isLoading.value = false
  }
}

const handleSortChange = (value: 'Recently' | 'Most Forked' | 'Most Used') => {
  emit('update:filterState', {
    ...props.filterState,
    sort: value
  })
  emit('update:showSortPopover', false)
}

const handleModelTypeChange = (type: string) => {
  if (props.modelType) return
  const types = [...props.filterState.model_types]
  const index = types.indexOf(type)
  if (index === -1) {
    types.push(type)
  } else {
    types.splice(index, 1)
  }
  emit('update:filterState', {
    ...props.filterState,
    model_types: types
  })
}

const handleBaseModelChange = (model: string) => {
  const index = selectedBaseModels.value.indexOf(model)
  if (index === -1) {
    selectedBaseModels.value.push(model)
  } else {
    selectedBaseModels.value.splice(index, 1)
  }

  const models = [...props.filterState.base_models]
  const modelIndex = models.indexOf(model)
  if (modelIndex === -1) {
    models.push(model)
  } else {
    models.splice(modelIndex, 1)
  }
  emit('update:filterState', {
    ...props.filterState,
    base_models: models
  })
}

const handleSearch = () => {
  emit('update:filterState', {
    ...props.filterState,
    keyword: props.filterState.keyword
  })
}

onMounted(async () => {
  if (props.selectedBaseModels) {
    selectedBaseModels.value = [...props.selectedBaseModels]
  }
  await getFilterData()
})
</script>

<template>
  <div class="flex space-x-2 mb-4">
    <div class="relative flex-1">
      <Input v-model="filterState.keyword" v-debounce="handleSearch" placeholder="Filter by name"
        class="h-[44px] border border-[#9CA3AF] w-full bg-[#222] rounded-lg pr-8 pl-8" />
      <span class="absolute start-0 inset-y-0 flex items-center justify-center px-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"
          class="hover:brightness-150 transition-all duration-300">
          <path
            d="M14 14L11.1333 11.1333M12.6667 7.33333C12.6667 10.2789 10.2789 12.6667 7.33333 12.6667C4.38781 12.6667 2 10.2789 2 7.33333C2 4.38781 4.38781 2 7.33333 2C10.2789 2 12.6667 4.38781 12.6667 7.33333Z"
            stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </span>
    </div>

    <Popover class="bg-[#353535] z-[5100]" :open="showSortPopover"
      @update:open="emit('update:showSortPopover', $event)">
      <PopoverTrigger>
        <Button variant="default" class="w-[44px] h-[44px] hover:border-2 hover:border-white cursor-pointer group">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M2 10.6667L4.66667 13.3334M4.66667 13.3334L7.33333 10.6667M4.66667 13.3334V2.66675M7.33333 2.66675H14M7.33333 5.33341H12M7.33333 8.00008H10"
              stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </Button>
      </PopoverTrigger>

      <PopoverContent side="bottom" align="end" class="w-[150px] p-0 bg-[#353535] rounded-lg">
        <Command>
          <CommandList>
            <CommandGroup>
              <CommandItem value="recently" @click="handleSortChange('Recently')" :class="[
                'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                filterState.sort === 'Recently' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
              ]">
                Recently
              </CommandItem>
              <CommandItem v-if="!['my', 'my_fork'].includes(mode)" value="most-forked"
                @click="handleSortChange('Most Forked')" :class="[
                  'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                  filterState.sort === 'Most Forked' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
                ]">
                Most Forked
              </CommandItem>
              <CommandItem v-if="!['my', 'my_fork'].includes(mode)" value="most-used"
                @click="handleSortChange('Most Used')" :class="[
                  'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                  filterState.sort === 'Most Used' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
                ]">
                Most Used
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>

    <Popover class="z-[5100]">
      <PopoverTrigger>
        <Button variant="default" class="w-[44px] h-[44px] hover:border-2 hover:border-white cursor-pointer">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none" class="mr-2">
            <path d="M14.6666 2H1.33325L6.66658 8.30667V12.6667L9.33325 14V8.30667L14.6666 2Z" stroke="#F9FAFB"
              stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </Button>
      </PopoverTrigger>

      <PopoverContent side="bottom" align="end" class="w-[200px] p-0 bg-[#222] rounded-lg">
        <Command>
          <CommandList>
            <CommandGroup>
              <div class="p-2">
                <div class="text-sm font-medium text-[#F9FAFB] mb-2">Model Types</div>
              </div>
              <CommandItem value="model-types" class="p-2">
                <div class="flex flex-wrap gap-2">
                  <Badge variant="secondary" v-for="type in modelTypes" :key="type.value"
                    @click="handleModelTypeChange(type.value)" :class="[
                      'cursor-pointer hover:!bg-inherit',
                      filterState.model_types.includes(type.value) || modelType === type.value
                        ? 'bg-[#6D28D9] hover:!bg-[#6D28D9]'
                        : 'bg-[#4E4E4E] hover:!bg-[#4E4E4E]'
                    ]">
                    {{ type.label }}
                  </Badge>
                </div>
              </CommandItem>
            </CommandGroup>
            <CommandSeparator />
            <CommandGroup>
              <div class="p-2">
                <div class="text-sm font-medium text-[#F9FAFB] mb-2">Base Models</div>
              </div>
              <CommandItem value="base-models" class="p-2">
                <div class="flex flex-wrap gap-2">
                  <Badge variant="secondary"
                    v-for="model in baseModelTypes.filter(m => props.selectedBaseModels?.includes(m.value))"
                    :key="model.value" @click="handleBaseModelChange(model.value)" :class="[
                      'cursor-pointer hover:!bg-inherit',
                      selectedBaseModels.includes(model.value) ? 'bg-[#6D28D9] hover:!bg-[#6D28D9]' : 'bg-[#4E4E4E] hover:!bg-[#4E4E4E]'
                    ]">
                    {{ model.label }}
                  </Badge>
                </div>
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  </div>
</template>