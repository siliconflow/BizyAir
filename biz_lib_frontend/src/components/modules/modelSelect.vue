<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent
} from '@/components/ui/tabs'
import {
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog'
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

interface Model {
  name: string
  version: string
  baseModel: string
  status: string
  isPublic?: boolean
  isCheckpoint?: boolean
  versions?: { version: string, baseModel: string, status: string }[]
}

interface FilterState {
  mode: 'my' | 'my_fork' | 'publicity'
  keyword: string
  modelTypes: string[]
  baseModels: string[]
  sort: 'recently' | 'most-forked' | 'most-used'
}

const filterState = ref<FilterState>({
  mode: 'my',
  keyword: '',
  modelTypes: [],
  baseModels: [],
  sort: 'recently'
})

const models = ref<Model[]>([
  {
    name: 'Model A',
    version: 'V1.0',
    baseModel: 'SDXL 1.0',
    status: 'Available',
    isPublic: true,
    isCheckpoint: true,
    versions: [{
      version: 'V1.0',
      baseModel: 'SDXL 1.0',
      status: 'Available'
    }, {
      version: 'V1.1',
      baseModel: 'SDXL 1.1',
      status: 'Unavailable',
    }]
  },
  {
    name: 'Model B',
    version: 'V1.1',
    baseModel: 'SDXL 1.1',
    status: 'Unavailable',
    versions: [{
      version: 'V1.00000000000000000000000000000000000000000000000000000',
      baseModel: 'SDXL 1.0',
      status: 'Available'
    }, {
      version: 'V1.1',
      baseModel: 'SDXL 1.1',
      status: 'Unavailable',
    }]
  },
  {
    name: 'Model C',
    version: 'V1.0',
    baseModel: 'SDXL 1.0',
    status: 'Available',
    versions: [{
      version: 'V1.0',
      baseModel: 'SDXL 1.0',
      status: 'Available'
    }, {
      version: 'V1.1',
      baseModel: 'SDXL 1.1',
      status: 'Available',
    }]
  },


])

// const props = defineProps<{
//   comfyUIApp?: any,
//   nodeId?: string,
//   widgetName?: string
// }>()


const expandedModels = ref<Set<string>>(new Set([models.value[0].name]))

const toggleExpand = (modelName: string) => {
  if (expandedModels.value.has(modelName)) {
    expandedModels.value.delete(modelName)
  } else {
    expandedModels.value.add(modelName)
  }
}

const handleSortChange = (value: 'recently' | 'most-forked' | 'most-used') => {
  filterState.value.sort = value
}
</script>

<template>
  <div class="p-2 font-['Inter']">
    <DialogTitle class="text-xl font-bold">Select Model</DialogTitle>
    <DialogDescription class="text-sm text-gray-500">

    </DialogDescription>

    <div class="flex items-center justify-end mb-4">
      <Button variant="ghost" class="h-8 w-8 p-0">
        <span class="sr-only">Close</span>
      </Button>
    </div>

    <Tabs defaultValue="my-posts" class="mb-4">

      <TabsList class="grid w-full grid-cols-3 h-12 bg-[#4E4E4E] text-sm">
        <TabsTrigger value="my-posts"
          class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">My
          Models
        </TabsTrigger>
        <TabsTrigger value="my-forks"
          class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">My
          Forks
        </TabsTrigger>
        <TabsTrigger value="community"
          class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2">
          Community Models
        </TabsTrigger>
      </TabsList>
      <TabsContent value="my-posts">
        <div class="flex space-x-2 mb-4">
          <div class="relative flex-1">
            <Input v-model="filterState.keyword" placeholder="Filter by name"
              class="h-[44px] border border-[#9CA3AF]  w-full bg-[#222] rounded-lg pr-8" />
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"
              class="absolute right-2 top-1/2 -translate-y-1/2 ">
              <path
                d="M14 14L11.1333 11.1333M12.6667 7.33333C12.6667 10.2789 10.2789 12.6667 7.33333 12.6667C4.38781 12.6667 2 10.2789 2 7.33333C2 4.38781 4.38781 2 7.33333 2C10.2789 2 12.6667 4.38781 12.6667 7.33333Z"
                stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <Popover class="bg-[#353535]">
            <PopoverTrigger>
              <Button variant="default"
                class="w-[44px] h-[44px] hover:border-2 hover:border-white cursor-pointer group">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path
                    d="M2 10.6667L4.66667 13.3334M4.66667 13.3334L7.33333 10.6667M4.66667 13.3334V2.66675M7.33333 2.66675H14M7.33333 5.33341H12M7.33333 8.00008H10"
                    stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </Button>
            </PopoverTrigger>
            <PopoverContent side="bottom" align="end" class="w-[150px] p-0 bg-[#353535] rounded-lg group-hover:visible">
              <Command>
                <CommandList>
                  <CommandGroup>
                    <CommandItem value="recently" @click="handleSortChange('recently')"
                      :class="['px-2 py-1.5 mb-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]', filterState.sort === 'recently' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : '']">
                      Recently
                    </CommandItem>
                    <CommandSeparator />
                    <CommandItem value="most-forked" @click="handleSortChange('most-forked')"
                      :class="['px-2 py-1.5 mb-1 mt-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]', filterState.sort === 'most-forked' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : '']">
                      Most Forked</CommandItem>
                    <CommandSeparator />
                    <CommandItem value="most-used" @click="handleSortChange('most-used')"
                      :class="['px-2 py-1.5 mt-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]', filterState.sort === 'most-used' ? '!bg-[#6D28D9] !text-[#F9FAFB]' : '']">
                      Most Used</CommandItem>
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>

          <Popover>
            <PopoverTrigger>
              <Button variant="default" class="w-[44px] h-[44px] hover:border-2 hover:border-white cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"
                  class="mr-2">
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
                        <Badge variant="secondary" class="cursor-pointer hover:bg-[#6D28D9]">Checkpoint</Badge>
                        <Badge variant="secondary" class="cursor-pointer hover:bg-[#6D28D9]">LoRA</Badge>
                        <Badge variant="secondary" class="cursor-pointer hover:bg-[#6D28D9]">TextualInversion</Badge>
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
                        <Badge variant="secondary" class="cursor-pointer hover:bg-[#6D28D9]">SDXL 1.0</Badge>
                        <Badge variant="secondary" class="cursor-pointer hover:bg-[#6D28D9]">SDXL 1.1</Badge>
                        <Badge variant="secondary" class="cursor-pointer hover:bg-[#6D28D9]">SD 1.5</Badge>
                        <Badge variant="secondary" class="cursor-pointer hover:bg-[#6D28D9]">SD 2.1</Badge>
                      </div>
                    </CommandItem>
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </div>
        <ScrollArea class="h-[500px] rounded-md border-0">
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
              <template v-for="model in models" :key="model.name + model.version">
                <TableRow class="group cursor-pointer border-[#F9FAFB]/60 hover:bg-transparent h-12">
                  <TableCell class="w-[40%]" @click="toggleExpand(model.name)">
                    <div class="flex items-center space-x-2">
                      <span class="text-lg">
                        <font-awesome-icon
                          :icon="['fas', expandedModels.has(model.name) ? 'angle-down' : 'angle-right']" />
                      </span>
                      <span>{{ model.name }}</span>
                      <Badge v-if="model.isCheckpoint" variant="default">Checkpoint</Badge>
                    </div>
                  </TableCell>
                  <TableCell class="w-[25%]">-</TableCell>
                  <TableCell class="w-[20%]">-</TableCell>
                  <TableCell class="w-[15%]">
                    <div class="flex justify-end h-full">
                      <div class="flex justify-center items-center hover:bg-[#222222] rounded-md w-8 h-8">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                          <path fill="white"
                            d="M12 16a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2a2 2 0 0 1 2-2m0-6a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2a2 2 0 0 1 2-2m0-6a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2a2 2 0 0 1 2-2" />
                        </svg>
                      </div>
                    </div>
                  </TableCell>
                </TableRow>
                <template v-if="expandedModels.has(model.name) && model.versions">
                  <TableRow v-for="version in model.versions" :key="version.version"
                    class="bg-[#3D3D3D] hover:bg-[#4E4E4E] border-[#F9FAFB]/60 h-12">
                    <TableCell class="pl-10 w-[40%] max-w-[200px]">
                      <div class="text-sm text-white-500 flex items-center min-w-0">
                        <span class="truncate flex-1">{{ version.version }}</span>
                        <div class="flex-shrink-0 ml-2">
                          <svg v-if="version.status === 'Available'" xmlns="http://www.w3.org/2000/svg" width="16"
                            height="17" viewBox="0 0 16 17" fill="none">
                            <path
                              d="M1.33325 8.49992C1.33325 8.49992 3.33325 3.83325 7.99992 3.83325C12.6666 3.83325 14.6666 8.49992 14.6666 8.49992C14.6666 8.49992 12.6666 13.1666 7.99992 13.1666C3.33325 13.1666 1.33325 8.49992 1.33325 8.49992Z"
                              stroke="#9CA3AF" stroke-linecap="round" stroke-linejoin="round" />
                            <path
                              d="M7.99992 10.4999C9.10449 10.4999 9.99992 9.60449 9.99992 8.49992C9.99992 7.39535 9.10449 6.49992 7.99992 6.49992C6.89535 6.49992 5.99992 7.39535 5.99992 8.49992C5.99992 9.60449 6.89535 10.4999 7.99992 10.4999Z"
                              stroke="#9CA3AF" stroke-linecap="round" stroke-linejoin="round" />
                          </svg>
                          <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17"
                            fill="none">
                            <path
                              d="M6.58658 7.08659C6.39009 7.26968 6.23248 7.49048 6.12317 7.73582C6.01386 7.98115 5.95508 8.24598 5.95034 8.51452C5.9456 8.78307 5.995 9.04981 6.09559 9.29884C6.19618 9.54788 6.3459 9.7741 6.53582 9.96402C6.72573 10.1539 6.95196 10.3037 7.20099 10.4042C7.45003 10.5048 7.71677 10.5542 7.98531 10.5495C8.25385 10.5448 8.51869 10.486 8.76402 10.3767C9.00935 10.2674 9.23015 10.1097 9.41325 9.91325M7.15325 3.88659C7.43412 3.85159 7.71687 3.83378 7.99992 3.83325C12.6666 3.83325 14.6666 8.49992 14.6666 8.49992C14.3685 9.138 13.9947 9.73787 13.5533 10.2866M4.40659 4.90659C3.08075 5.80967 2.01983 7.05009 1.33325 8.49992C1.33325 8.49992 3.33325 13.1666 7.99992 13.1666C9.27719 13.17 10.5271 12.7967 11.5933 12.0933M1.33325 1.83325L14.6666 15.1666"
                              stroke="#9CA3AF" stroke-linecap="round" stroke-linejoin="round" />
                          </svg>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell class="w-25 truncate block">{{ version.baseModel }}</TableCell>
                    <TableCell class="w-[20%]">{{ version.status }}</TableCell>
                    <TableCell class="w-[15%] flex justify-start">
                      <Button :variant="'default'" :disabled="version.status !== 'Available'"
                        :class="{ 'opacity-50': version.status !== 'Available' }">
                        Apply
                      </Button>
                    </TableCell>
                  </TableRow>
                </template>
              </template>
            </TableBody>
          </Table>
        </ScrollArea>
        <div class="flex justify-between items-center mt-4">
          <Button variant="ghost" size="sm">Previous</Button>
          <span class="text-sm text-gray-500">Page 1 of 5</span>
          <Button variant="ghost" size="sm">Next</Button>
        </div>
      </TabsContent>
      <TabsContent value="my-forks">
        <!-- My Forks content -->
      </TabsContent>
      <TabsContent value="community">
        <!-- Community content -->
      </TabsContent>

    </Tabs>
  </div>
</template>