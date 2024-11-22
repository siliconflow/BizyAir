<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { onMounted, ref } from 'vue'
import { modelStore } from '@/stores/modelStatus'
import type { SortValue } from '@/types/model'
const modelStoreInstance = modelStore()
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

const selectedBaseModels = ref<string[]>([])

interface Props {
  showSortPopover: boolean
}

interface Emits {
  (e: 'update:showSortPopover', value: boolean): void
  (e: 'fetchData'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const handleSortChange = (value: SortValue) => {
  modelStoreInstance.filterState.sort = value
  emit('fetchData')
  emit('update:showSortPopover', false)
}

const handleModelTypeChange = (type: string) => {
  if (modelStoreInstance.selectedBaseModels.length !== 0) return

  const types = [...modelStoreInstance.filterState.model_types]
  const index = types.indexOf(type)
  index === -1 ? types.push(type) : types.splice(index, 1)

  modelStoreInstance.filterState.model_types = types
  emit('fetchData')
  emit('update:showSortPopover', false)
}

const handleBaseModelChange = (model: string) => {
  const index = selectedBaseModels.value.indexOf(model)
  if (index === -1) {
    selectedBaseModels.value.push(model)
  } else {
    selectedBaseModels.value.splice(index, 1)
  }

  const models = [...modelStoreInstance.filterState.base_models]
  const modelIndex = models.indexOf(model)
  if (modelIndex === -1) {
    models.push(model)
  } else {
    models.splice(modelIndex, 1)
  }
  modelStoreInstance.filterState.base_models = models
  emit('fetchData')
  emit('update:showSortPopover', false)
}

const handleSearch = () => {
  modelStoreInstance.modelListPathParams.current = 1
  emit('fetchData')
  emit('update:showSortPopover', false)
}

onMounted(async () => {
  if (modelStoreInstance.selectedBaseModels) {
    selectedBaseModels.value = [...modelStoreInstance.selectedBaseModels]
  }
})
</script>

<template>
  <div class="flex space-x-2 mb-4">
    <div class="relative flex-1">
      <Input v-model="modelStoreInstance.filterState.keyword" v-debounce="handleSearch" placeholder="Filter by name"
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
      <PopoverTrigger class="bg-transparent">
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
                modelStoreInstance.filterState.sort === 'Recently' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
              ]">
                Recently
              </CommandItem>
              <CommandItem v-if="!['my', 'my_fork'].includes(modelStoreInstance.mode)" value="most-forked"
                @click="handleSortChange('Most Forked')" :class="[
                  'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                  modelStoreInstance.filterState.sort === 'Most Forked' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
                ]">
                Most Forked
              </CommandItem>
              <CommandItem v-if="!['my', 'my_fork'].includes(modelStoreInstance.mode)" value="most-used"
                @click="handleSortChange('Most Used')" :class="[
                  'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                  modelStoreInstance.filterState.sort === 'Most Used' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
                ]">
                Most Used
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>

    <Popover class="z-[5100]">
      <PopoverTrigger class="bg-transparent">
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
                  <Badge variant="secondary" v-for="type in modelStoreInstance.modelTypes" :key="type.value"
                    @click="handleModelTypeChange(type.value)" :class="[
                      'cursor-not-allowed hover:!bg-inherit',
                      modelStoreInstance.filterState.model_types.includes(type.value)
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
                    v-for="model in modelStoreInstance.baseModelTypes.filter((m: any) => modelStoreInstance.selectedBaseModels?.includes(m.value))"
                    :key="model.value" @click="handleBaseModelChange(model.value)" :class="[
                      'cursor-pointer hover:!bg-inherit',
                      modelStoreInstance.filterState.base_models.includes(model.value) ? 'bg-[#6D28D9] hover:!bg-[#6D28D9]' : 'bg-[#4E4E4E] hover:!bg-[#4E4E4E]'
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
