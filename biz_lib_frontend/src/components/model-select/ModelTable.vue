<script setup lang="ts">
import { ref, PropType, onMounted } from 'vue'
import { useToast } from '@/components/ui/toast/use-toast'
import { Badge } from '@/components/ui/badge'
import { remove_model } from '@/api/model'
import Toaster from '@/components/ui/toast/Toaster.vue'
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

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import type { Model, ModelVersion } from '@/types/model'
import ModelVersionRow from './ModelVersionRow.vue'


const props = defineProps({
  models: {
    type: Array as PropType<Model[]>,
    required: true
  },
  mode: {
    type: String,
    required: true
  }
})
const { toast } = useToast()
const expandedModels = ref<Set<string>>(new Set())
const currentOperateModel = ref<string>('')

onMounted(() => {
  if (props.models.length > 0) {
    expandedModels.value.add(props.models[0].name)
  }
})

const toggleExpand = (modelName: string) => {
  if (expandedModels.value.has(modelName)) {
    expandedModels.value.delete(modelName)
  } else {
    expandedModels.value.add(modelName)
  }
}

const handleOperateChange = (value: 'edit' | 'remove', { id, name, versions }: Model) => {
  currentOperateModel.value = name
  if (value === 'edit') {
    currentOperateModel.value = ''
  }
  if (value === 'remove') {
    if (versions) {
      const hasPublic = versions.some((version) => version.public)
      if (hasPublic) {
        toast({
          description: 'Model has public version, cannot remove.',
        })
        return
      }
    }


    handleRemoveModel(id)
  }
}

const handleRemoveModel = (id: string) => {
  remove_model(id).then((_) => {
    toast({
      description: 'Model removed successfully.',
    })
    emit('remove')
  })
}

const emit = defineEmits(['apply', 'remove'])
const handleApply = (version: ModelVersion) => {
  emit('apply', version)
}
</script>
<template>
  <div class="min-h-[400px]">
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
        <template v-if="props.models.length === 0">
          <TableRow>
            <TableCell colspan="4" class="h-[360px]">
              <div class="flex items-center justify-center h-full text-gray-500">
                No data available
              </div>
            </TableCell>
          </TableRow>
        </template>
        <template v-else>
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
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17"
                      fill="none">
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
                  <Popover v-if="props.mode === 'my' || props.mode === 'my_fork'" class="bg-[#353535]"
                    :open="currentOperateModel === model.name"
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
                            <CommandItem value="edit" @click="handleOperateChange('edit', model)"
                              class="px-2 py-1.5 mb-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]">
                              Edit
                            </CommandItem>
                            <CommandSeparator />
                            <CommandItem value="remove"
                              class="px-2 py-1.5 mb-1 mt-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]">
                              <AlertDialog>
                                <AlertDialogTrigger>Remove</AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      This action cannot be undone. This will permanently delete the model.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction @click="handleOperateChange('remove', model)">Continue
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
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
                :mode="props.mode" @apply="handleApply" />
            </template>
          </template>
        </template>
      </TableBody>
    </Table>
  </div>
  <Toaster />
</template>