<script setup lang="ts">
import { ref, PropType } from 'vue'

import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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
import type { Model, ModelVersion } from '@/types/model'
import ModelVersionRow from './ModelVersionRow.vue'


const props = defineProps({
  models: {
    type: Array as PropType<Model[]>,
    required: true
  }
})

const expandedModels = ref<Set<string>>(new Set())
const currentOperateModel = ref<string>('')

const toggleExpand = (modelName: string) => {
  if (expandedModels.value.has(modelName)) {
    expandedModels.value.delete(modelName)
  } else {
    expandedModels.value.add(modelName)
  }
}

const handleOperateChange = (value: 'edit' | 'remove', modelName: string) => {
  currentOperateModel.value = modelName
  if (value === 'edit') {
    currentOperateModel.value = ''
  }
}

const emit = defineEmits(['apply'])
const handleApply = (version: ModelVersion) => {
  emit('apply', version)
}
</script>
<template>
  <Table>
    <TableHeader>
      <TableRow class="hover:bg-transparent border-[#F9FAFB]/60">
        <TableHead class="w-[40%]">Name</TableHead>
        <TableHead class="w-[25%]">Base Model</TableHead>
        <TableHead class="w-[20%]">Status</TableHead>
        <TableHead class="w-[15%]">Operate</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <template v-for="model in props.models" :key="model.name + model.id">
        <TableRow class="group cursor-pointer border-[#F9FAFB]/60 hover:bg-transparent h-12">
          <TableCell class="w-[40%]" @click="toggleExpand(model.name)">
            <div class="flex items-center space-x-2">
              <span class="text-lg">
                <svg v-if="expandedModels.has(model.name)" xmlns="http://www.w3.org/2000/svg" width="16" height="17"
                  viewBox="0 0 16 17" fill="none">
                  <path d="M4 6L8 10L12 6" stroke="#F9FAFB" stroke-width="1.5" stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17" fill="none">
                  <path d="M6 4L10 8L6 12" stroke="#F9FAFB" stroke-width="1.5" stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </span>
              <span>{{ model.name }}</span>
              <Badge variant="default">{{ model.type }}</Badge>
            </div>
          </TableCell>
          <TableCell class="w-[25%]">-</TableCell>
          <TableCell class="w-[20%]">-</TableCell>
          <TableCell class="w-[15%]">
            <div class="flex justify-end h-full">
              <Popover class="bg-[#353535]" :open="currentOperateModel === model.name"
                @update:open="(value) => value ? currentOperateModel = model.name : currentOperateModel = ''">
                <PopoverTrigger>
                  <div class="flex justify-center items-center hover:bg-[#222222] rounded-md w-8 h-8">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                      <path fill="white"
                        d="M12 16a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2a2 2 0 0 1 2-2m0-6a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2a2 2 0 0 1 2-2m0-6a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2a2 2 0 0 1 2-2" />
                    </svg>
                  </div>
                </PopoverTrigger>
                <PopoverContent side="bottom" align="end"
                  class="w-[150px] p-0 bg-[#353535] rounded-lg group-hover:visible">
                  <Command>
                    <CommandList>
                      <CommandGroup>
                        <CommandItem value="edit" @click="handleOperateChange('edit', model.name)"
                          class="px-2 py-1.5 mb-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]">
                          Edit
                        </CommandItem>
                        <CommandSeparator />
                        <CommandItem value="remove" @click="handleOperateChange('remove', model.name)"
                          class="px-2 py-1.5 mb-1 mt-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]">
                          Remove
                        </CommandItem>
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>
          </TableCell>
        </TableRow>
        <template v-if="expandedModels.has(model.name) && model.versions">
          <ModelVersionRow v-for="version in model.versions" :key="version.version" :version="version"
            @apply="handleApply" />
        </template>
      </template>
    </TableBody>
  </Table>
</template>