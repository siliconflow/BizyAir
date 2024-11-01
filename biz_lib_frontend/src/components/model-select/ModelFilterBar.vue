<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
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
import type { FilterState } from '@/types/model'

interface Props {
  filterState: FilterState
  showSortPopover: boolean
}

interface Emits {
  (e: 'update:filterState', value: FilterState): void
  (e: 'update:showSortPopover', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleSortChange = (value: 'recently' | 'most-forked' | 'most-used') => {
  emit('update:filterState', {
    ...props.filterState,
    sort: value
  })
  emit('update:showSortPopover', false)
}

const handleModelTypeChange = (type: string) => {
  const types = [...props.filterState.modelTypes]
  const index = types.indexOf(type)
  if (index === -1) {
    types.push(type)
  } else {
    types.splice(index, 1)
  }
  emit('update:filterState', {
    ...props.filterState,
    modelTypes: types
  })
}

const handleBaseModelChange = (model: string) => {
  const models = [...props.filterState.baseModels]
  const index = models.indexOf(model)
  if (index === -1) {
    models.push(model)
  } else {
    models.splice(index, 1)
  }
  emit('update:filterState', {
    ...props.filterState,
    baseModels: models
  })
}

const updateKeyword = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:filterState', {
    ...props.filterState,
    keyword: target.value
  })
}
</script>

<template>
  <div class="flex space-x-2 mb-4">
    <div class="relative flex-1">
      <Input :value="filterState.keyword" @input="updateKeyword" placeholder="Filter by name"
        class="h-[44px] border border-[#9CA3AF] w-full bg-[#222] rounded-lg pr-8" />
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"
        class="absolute right-2 top-1/2 -translate-y-1/2">
        <path
          d="M14 14L11.1333 11.1333M12.6667 7.33333C12.6667 10.2789 10.2789 12.6667 7.33333 12.6667C4.38781 12.6667 2 10.2789 2 7.33333C2 4.38781 4.38781 2 7.33333 2C10.2789 2 12.6667 4.38781 12.6667 7.33333Z"
          stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </div>

    <Popover class="bg-[#353535]" :open="showSortPopover" @update:open="emit('update:showSortPopover', $event)">
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
              <CommandItem value="recently" @click="handleSortChange('recently')" :class="[
                'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                filterState.sort === 'recently' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
              ]">
                Recently
              </CommandItem>
              <CommandItem value="most-forked" @click="handleSortChange('most-forked')" :class="[
                'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                filterState.sort === 'most-forked' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
              ]">
                Most Forked
              </CommandItem>
              <CommandItem value="most-used" @click="handleSortChange('most-used')" :class="[
                'px-2 py-1.5 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]',
                filterState.sort === 'most-used' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : ''
              ]">
                Most Used
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>

    <Popover>
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
                  <Badge variant="secondary" @click="handleModelTypeChange('checkpoint')" :class="[
                    'cursor-pointer hover:bg-[#6D28D9]',
                    filterState.modelTypes.includes('checkpoint') ? 'bg-[#6D28D9]' : ''
                  ]">
                    Checkpoint
                  </Badge>
                  <Badge variant="secondary" @click="handleModelTypeChange('lora')" :class="[
                    'cursor-pointer hover:bg-[#6D28D9]',
                    filterState.modelTypes.includes('lora') ? 'bg-[#6D28D9]' : ''
                  ]">
                    LoRA
                  </Badge>
                  <Badge variant="secondary" @click="handleModelTypeChange('textualinversion')" :class="[
                    'cursor-pointer hover:bg-[#6D28D9]',
                    filterState.modelTypes.includes('textualinversion') ? 'bg-[#6D28D9]' : ''
                  ]">
                    TextualInversion
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
                  <Badge variant="secondary" @click="handleBaseModelChange('SDXL 1.0')" :class="[
                    'cursor-pointer hover:bg-[#6D28D9]',
                    filterState.baseModels.includes('SDXL 1.0') ? 'bg-[#6D28D9]' : ''
                  ]">
                    SDXL 1.0
                  </Badge>
                  <Badge variant="secondary" @click="handleBaseModelChange('SDXL 1.1')" :class="[
                    'cursor-pointer hover:bg-[#6D28D9]',
                    filterState.baseModels.includes('SDXL 1.1') ? 'bg-[#6D28D9]' : ''
                  ]">
                    SDXL 1.1
                  </Badge>
                  <Badge variant="secondary" @click="handleBaseModelChange('SD 1.5')" :class="[
                    'cursor-pointer hover:bg-[#6D28D9]',
                    filterState.baseModels.includes('SD 1.5') ? 'bg-[#6D28D9]' : ''
                  ]">
                    SD 1.5
                  </Badge>
                  <Badge variant="secondary" @click="handleBaseModelChange('SD 2.1')" :class="[
                    'cursor-pointer hover:bg-[#6D28D9]',
                    filterState.baseModels.includes('SD 2.1') ? 'bg-[#6D28D9]' : ''
                  ]">
                    SD 2.1
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