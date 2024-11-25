<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useToaster } from '@/components/modules/toats/index'
import { Badge } from '@/components/ui/badge'
import { remove_model, model_detail } from '@/api/model'
import ModelPagination from './ModelPagination.vue'
import { modelStore } from '@/stores/modelStatus'
import { Loader2 } from 'lucide-vue-next'
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
import { useAlertDialog } from '@/components/modules/vAlertDialog/index'

import type { Model } from '@/types/model'
import ModelVersionRow from './ModelVersionRow.vue'


const modelStoreInstance = modelStore()


const expandedModels = ref<Set<string>>(new Set())
const currentOperateModel = ref<string>('')

const isLoading = computed(() => modelStoreInstance.isLoading)


watch(() => modelStoreInstance.models, (newModels: Model[]) => {
  if (newModels.length > 0) {
    expandedModels.value.clear()
    expandedModels.value.add(newModels[0].name)
  }
}, { deep: true })



const toggleExpand = (modelName: string) => {
  if (expandedModels.value.has(modelName)) {
    expandedModels.value.delete(modelName)
  } else {
    expandedModels.value.add(modelName)
  }
}

const handleOperateChange = async (value: 'edit' | 'remove', model: Model) => {
  const { id, name, versions } = model
  currentOperateModel.value = name
  if (value === 'edit') {
    const res = await model_detail({ id: model.id, source: modelStoreInstance.mode })
    modelStoreInstance.setModelDetail(res.data)
    modelStoreInstance.setDialogStatus(true)
    currentOperateModel.value = ''
  }
  if (value === 'remove') {
    const res = await useAlertDialog({
      title: 'Are you sure you want to delete this model?',
      desc: 'This action cannot be undone.',
      cancel: 'No, Keep It',
      continue: 'Yes, Delete It',
    })
    if (!res) return

    if (versions) {
      const hasPublic = versions.some((version) => version.public)
      if (hasPublic) {
        useToaster.warning('Model has public version, cannot remove.')
        return
      }
    }
    handleRemoveModel(id)
  }
}



const handleRemoveModel = async (id: string) => {
  try {
    await remove_model(id)
    useToaster.success('Model removed successfully.')
    modelStoreInstance.closeAndReload()
  } catch (error) {
    useToaster.error(`Failed to remove model. ${error}`)
  }
}

</script>
<template>
  <div>
    <Table>
      <TableHeader>
        <TableRow class="hover:bg-transparent border-[#F9FAFB]/60">
          <TableHead class="w-[55%]">Name</TableHead>
          <TableHead class="w-[15%]">Base Model</TableHead>
          <TableHead class="w-[15%]">Status</TableHead>
          <TableHead class="w-[15%]">Operate</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-if="isLoading">

          <TableRow class="bg-transparent hover:bg-transparent">
            <TableCell colspan="4" class="h-[400px]">
              <div class="flex items-center justify-center h-full ">
                <Loader2 class="h-8 w-8 animate-spin text-[#F9FAFB]" />
              </div>
            </TableCell>
          </TableRow>
        </template>
        <template v-else>
          <template v-if="!isLoading && modelStoreInstance.models.length > 0">
            <template v-for="model in modelStoreInstance.models" :key="`${model.id}-${model.name}`">
              <TableRow class="group cursor-pointer border-[#F9FAFB]/60 hover:bg-transparent h-12">
                <TableCell class="w-[55%]" @click="toggleExpand(model.name)">
                  <div class="flex items-center space-x-2">
                    <span class="text-sm">
                      <svg v-if="expandedModels.has(model.name)" xmlns="http://www.w3.org/2000/svg" width="16"
                        height="17" viewBox="0 0 16 17" fill="none">
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
                <TableCell class="w-[15%]">-</TableCell>
                <TableCell class="w-[15%]">-</TableCell>
                <TableCell class="w-[15%]">
                  <div class="flex justify-end h-full">
                    <Popover v-if="modelStoreInstance.mode === 'my' || modelStoreInstance.mode === 'my_fork'"
                      class="bg-[#353535] z-[5100]mmm" :open="currentOperateModel === model.name"
                      @update:open="(value: any) => value ? currentOperateModel = model.name : currentOperateModel = ''">
                      <PopoverTrigger class="bg-transparent">
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
                              <CommandItem value="remove" @click="handleOperateChange('remove', model)"
                                class="px-2 py-1.5 mb-1 mt-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]">
                                Remove
                              </CommandItem>
                            </CommandGroup>
                          </CommandList>
                        </Command>
                      </PopoverContent>
                    </Popover>
                    <div v-else class="w-8 h-8"></div>
                  </div>
                </TableCell>
              </TableRow>
              <template v-if="expandedModels.has(model.name) && model.versions">
                <ModelVersionRow v-for="version in model.versions" :model="model" :key="version.version"
                  :version="version" />
              </template>
            </template>
          </template>
          <template v-else>
            <TableRow class="hover:bg-transparent">
              <TableCell colspan="4" class="h-[400px]">
                <div class="flex items-center justify-center  h-full text-[#F9FAFB] ">
                  No available data
                </div>
              </TableCell>
            </TableRow>
          </template>
        </template>
      </TableBody>
    </Table>
    <div class="w-full flex justify-center mt-8">
      <ModelPagination v-if="!isLoading" />
    </div>
  </div>
</template>
