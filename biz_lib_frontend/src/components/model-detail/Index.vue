<script setup lang="ts">
import {
  Tabs,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'

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

import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { modelStore } from '@/stores/modelStatus'

import { sliceString, formatSize, formatNumber } from '@/utils/tool'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { ref, onMounted, nextTick } from 'vue'

import { useAlertDialog } from '@/components/modules/vAlertDialog/index'
import { MdPreview } from 'md-editor-v3';

import { Model, ModelVersion } from '@/types/model'
import { model_detail, like_model, fork_model, remove_model } from '@/api/model'
import { useToaster } from '@/components/modules/toats/index'
import 'md-editor-v3/lib/style.css';
const modelStoreInstance = modelStore()

const model = ref<Model>()
const currentVersion = ref<ModelVersion>()
const downloadOpen = ref(false)
const scrollViewportRef = ref<any | null>(null)

const props = defineProps<{
  modelId: string,
  version: ModelVersion
}>()

const fetchModelDetail = async () => {
  const res = await model_detail({ id: props.modelId, source: modelStoreInstance.mode })
  if (!res.data) {
    useToaster.error('Model not found.')
    modelStoreInstance.closeAndReload()
    return
  }
  model.value = res.data
  initializeScroll()
}

const initializeScroll = () => {
  if (model.value && model.value.versions && model.value.versions.length > 0) {
    if (props.version?.id) {
      const targetVersion = model.value.versions.find(v => v.id === props.version.id)
      if (targetVersion) {
        currentVersion.value = { ...targetVersion }
        nextTick(() => {
          scrollWithDelay(props.version?.id)
        })
      }
    } else {
      currentVersion.value = { ...model.value.versions[0] }
      nextTick(() => {
        if (currentVersion.value?.id) {
          scrollWithDelay(currentVersion.value.id)
        }
      })
    }
  }
}


onMounted(async () => {
  await fetchModelDetail()

})

const handleTabChange = (value: number) => {
  const version = model.value?.versions?.find(v => v.id === value)
  if (version) {
    currentVersion.value = version
  }
}

const handleDownload = () => {
  downloadOpen.value = !downloadOpen.value
}

const handleLike = async () => {
  await like_model(currentVersion.value?.id)
  fetchModelDetail()
}

const handleFork = async () => {
  await fork_model(currentVersion.value?.id)
  await fetchModelDetail()
}

const scrollToTab = (versionId: number) => {
  nextTick(() => {
    setTimeout(() => {
      if (!scrollViewportRef.value) return
      const viewport = scrollViewportRef.value.$el.querySelector('[data-radix-scroll-area-viewport]')
      const tabsList = viewport?.querySelector('[role="tablist"]')
      const targetTab = tabsList?.querySelector(`[role="tab"].version-tab-${versionId}`) as HTMLElement
      if (!viewport || !targetTab || !tabsList) return

      const tabs = Array.from(tabsList.querySelectorAll('[role="tab"]'))
      const totalWidth = tabs.reduce((sum: number, tab) => sum + (tab as HTMLElement).offsetWidth, 0)
        ; (tabsList as HTMLElement).style.width = `${totalWidth}px`

      const tabPosition = targetTab.offsetLeft
      const viewportWidth = viewport.clientWidth
      const tabWidth = targetTab.offsetWidth

      const scrollPosition = Math.max(0, tabPosition - (viewportWidth - tabWidth) / 2)

      viewport.scrollTo({
        left: scrollPosition,
        behavior: 'smooth'
      })
    }, 100)
  })
}

const scrollWithDelay = (versionId: number) => {
  setTimeout(() => {
    scrollToTab(versionId)
  }, 200)
}

const handleModelOperation = async (type: 'edit' | 'remove', id: string | number) => {
  if (type === 'edit') {
    modelStoreInstance.setModelDetail(model)
    modelStoreInstance.setDialogStatus(true, Number(currentVersion.value?.id))
    downloadOpen.value = false
  }
  if (type === 'remove') {
    const res = await useAlertDialog({
      title: 'Are you sure you want to delete this model?',
      desc: 'This action cannot be undone.',
      cancel: 'No, Keep It',
      continue: 'Yes, Delete It',
      z: 'z-9000'
    })
    if (!res) return

    if (model.value?.versions) {
      const hasPublic = model.value?.versions.some((version) => version.public)
      if (hasPublic) {
        useToaster.warning('Model has public version, cannot remove.')
        downloadOpen.value = false
        return
      }
    }
    handleRemoveModel(id)
  }
}


const handleRemoveModel = async (id: number | string) => {
  try {
    await remove_model(id)
    useToaster.success('Model removed successfully.')
    modelStoreInstance.reload += 1
  } catch (error) {
    useToaster.error('Failed to remove model.')
    console.error('Error removing model:', error)
  }


}


const handleApply = () => {
  if (currentVersion.value && model.value) {
    modelStoreInstance.setApplyObject(currentVersion.value, model.value)
  }
}

const handleCopy = async (sign: string) => {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(sign || '');
      useToaster.success('Copied successfully.')
    } else {
      const input = document.createElement('input');
      input.value = sign || '';
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
    }
  } catch (err) {
    useToaster.error('Copy failed.')
  }

}
</script>

<template>
  <div v-if="model"
    class="p-6 pb-12 flex flex-col gap-4 items-start justify-start min-w-[1000px]   relative shadow-[0px_20px_40px_0px_rgba(0,0,0,0.25)]">
    <div class="flex flex-col gap-1.5 items-start justify-start self-stretch shrink-0 relative">
      <div class="flex flex-row gap-2 items-center justify-start self-stretch shrink-0 relative">
        <div
          class="text-text-text-foreground text-left font-['Inter-SemiBold',_sans-serif] text-lg leading-[18px] font-semibold relative"
          style="letter-spacing: -0.025em">
          {{ sliceString(model?.name, 60) }}
        </div>
        <div class="flex flex-row gap-1 items-start justify-start shrink-0 relative">
          <div
            class="bg-[#6D28D933] rounded-radius-rounded-xl pr-1.5 pl-1.5 flex flex-row gap-1 items-center justify-center shrink-0 min-w-[40px] relative overflow-hidden">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3.33325 2L12.6666 8L3.33325 14V2Z" stroke="#F9FAFB" stroke-linecap="round"
                stroke-linejoin="round" />
            </svg>
            <div
              class="text-text-text-foreground text-left font-['Inter-Regular',_sans-serif] text-sm leading-5 font-normal relative flex-1">
              {{ formatNumber(model?.counter?.used_count) }}
            </div>
          </div>
        </div>
        <div
          class="bg-[#6D28D933] rounded-radius-rounded-xl pr-1.5 pl-1.5 flex flex-row gap-1 items-center justify-center shrink-0 min-w-[40px] relative overflow-hidden">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M7.99992 1.33325L10.0599 5.50659L14.6666 6.17992L11.3333 9.42659L12.1199 14.0133L7.99992 11.8466L3.87992 14.0133L4.66659 9.42659L1.33325 6.17992L5.93992 5.50659L7.99992 1.33325Z"
              stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div
            class="text-text-text-foreground text-left font-['Inter-Regular',_sans-serif] text-sm leading-5 font-normal relative flex-1">
            {{ formatNumber(model?.counter?.forked_count) }}
          </div>
        </div>
        <div
          class="bg-[#6D28D933] rounded-radius-rounded-xl pr-1.5 pl-1.5 flex flex-row gap-1 items-center justify-center shrink-0 min-w-[40px] relative overflow-hidden">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <g clip-path="url(#clip0_315_3742)">
              <path
                d="M4.66659 6.66658V14.6666M9.99992 3.91992L9.33325 6.66658H13.2199C13.4269 6.66658 13.6311 6.71478 13.8162 6.80735C14.0013 6.89992 14.1624 7.03432 14.2866 7.19992C14.4108 7.36551 14.4947 7.55775 14.5317 7.7614C14.5688 7.96506 14.5579 8.17454 14.4999 8.37325L12.9466 13.7066C12.8658 13.9835 12.6974 14.2268 12.4666 14.3999C12.2358 14.573 11.9551 14.6666 11.6666 14.6666H2.66659C2.31296 14.6666 1.97382 14.5261 1.72378 14.2761C1.47373 14.026 1.33325 13.6869 1.33325 13.3333V7.99992C1.33325 7.6463 1.47373 7.30716 1.72378 7.05711C1.97382 6.80706 2.31296 6.66658 2.66659 6.66658H4.50659C4.75464 6.66645 4.99774 6.59713 5.20856 6.4664C5.41937 6.33567 5.58953 6.14873 5.69992 5.92659L7.99992 1.33325C8.3143 1.33715 8.62374 1.41203 8.90512 1.55232C9.1865 1.6926 9.43254 1.89466 9.62486 2.14339C9.81717 2.39212 9.9508 2.68109 10.0157 2.98872C10.0807 3.29635 10.0753 3.61468 9.99992 3.91992Z"
                stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
            </g>
            <defs>
              <clipPath id="clip0_315_3742">
                <rect width="16" height="16" fill="white" />
              </clipPath>
            </defs>
          </svg>
          <div
            class="text-text-text-foreground text-left font-['Inter-Regular',_sans-serif] text-sm leading-5 font-normal relative flex-1">
            {{ formatNumber(model?.counter?.liked_count) }}
          </div>
        </div>
      </div>
      <div class="flex flex-row gap-1 items-center justify-start self-stretch shrink-0 relative">
        <div
          class="bg-[#4e4e4e] rounded-lg p-1 flex flex-row gap-4 items-start justify-start self-stretch shrink-0 relative">
          <div class="min-w-[200px] max-w-[600px]">
            <ScrollArea ref="scrollViewportRef" class="rounded-md w-full">
              <div class="whitespace-nowrap">
                <Tabs :defaultValue="currentVersion?.id" :value="currentVersion?.id">
                  <TabsList class="inline-flex h-12  bg-transparent text-sm text-white w-auto">
                    <TabsTrigger v-for="version in model?.versions" :value="version.id"
                      @click="handleTabChange(version.id)" :class="['version-tab', `version-tab-${version.id}`]"
                      class="text-sm t bg-[#9CA3AF] data-[state=active]:bg-[#7C3AED] h-10 px-3 py-2 mx-1">

                      {{ version.version }}
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
              <ScrollBar orientation="horizontal" />
            </ScrollArea>
          </div>
        </div>
        <div
          class="text-text-text-muted-foreground text-left font-['Inter-Regular',_sans-serif] text-xs leading-5 font-normal relative flex-1">
        </div>
        <div class="flex gap-8 ">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"
            class="cursor-pointer" @click="handleLike"
            :style="{ stroke: currentVersion?.liked ? '#6D28D9' : '#F9FAFB', fill: currentVersion?.liked ? '#6D28D9' : 'none' }">
            <g clip-path="url(#clip0_440_1289)">
              <path
                d="M4.66659 6.66658V14.6666M9.99992 3.91992L9.33325 6.66658H13.2199C13.4269 6.66658 13.6311 6.71478 13.8162 6.80735C14.0013 6.89992 14.1624 7.03432 14.2866 7.19992C14.4108 7.36551 14.4947 7.55775 14.5317 7.7614C14.5688 7.96506 14.5579 8.17454 14.4999 8.37325L12.9466 13.7066C12.8658 13.9835 12.6974 14.2268 12.4666 14.3999C12.2358 14.573 11.9551 14.6666 11.6666 14.6666H2.66659C2.31296 14.6666 1.97382 14.5261 1.72378 14.2761C1.47373 14.026 1.33325 13.6869 1.33325 13.3333V7.99992C1.33325 7.6463 1.47373 7.30716 1.72378 7.05711C1.97382 6.80706 2.31296 6.66658 2.66659 6.66658H4.50659C4.75464 6.66645 4.99774 6.59713 5.20856 6.4664C5.41937 6.33567 5.58953 6.14873 5.69992 5.92659L7.99992 1.33325C8.3143 1.33715 8.62374 1.41203 8.90512 1.55232C9.1865 1.6926 9.43254 1.89466 9.62486 2.14339C9.81717 2.39212 9.9508 2.68109 10.0157 2.98872C10.0807 3.29635 10.0753 3.61468 9.99992 3.91992Z"
                stroke-linecap="round" stroke-linejoin="round" />
            </g>
            <defs>
              <clipPath id="clip0_440_1289">
                <rect width="16" height="16" fill="white" />
              </clipPath>
            </defs>
          </svg>


          <Popover v-if="modelStoreInstance.mode === 'my' || modelStoreInstance.mode === 'my_fork'"
            class="bg-[#353535] " :open="downloadOpen" @update:open="handleDownload">
            <PopoverTrigger class="bg-transparent">
              <div class="flex justify-center items-center  rounded-md w-8 relative z-50">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"
                  class="cursor-pointer">
                  <path
                    d="M8.66659 7.99992C8.66659 7.63173 8.36811 7.33325 7.99992 7.33325C7.63173 7.33325 7.33325 7.63173 7.33325 7.99992C7.33325 8.36811 7.63173 8.66659 7.99992 8.66659C8.36811 8.66659 8.66659 8.36811 8.66659 7.99992Z"
                    stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
                  <path
                    d="M8.66659 3.33325C8.66659 2.96506 8.36811 2.66658 7.99992 2.66658C7.63173 2.66658 7.33325 2.96506 7.33325 3.33325C7.33325 3.70144 7.63173 3.99992 7.99992 3.99992C8.36811 3.99992 8.66659 3.70144 8.66659 3.33325Z"
                    stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
                  <path
                    d="M8.66659 12.6666C8.66659 12.2984 8.36811 11.9999 7.99992 11.9999C7.63173 11.9999 7.33325 12.2984 7.33325 12.6666C7.33325 13.0348 7.63173 13.3333 7.99992 13.3333C8.36811 13.3333 8.66659 13.0348 8.66659 12.6666Z"
                    stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </PopoverTrigger>
            <PopoverContent side="bottom" align="end"
              class="w-[150px] p-0 bg-[#353535] rounded-lg group-hover:visible z-[9000]">
              <Command>
                <CommandList>
                  <CommandGroup>
                    <CommandItem value="edit" @click="handleModelOperation('edit', model?.id)"
                      class="px-2 py-1.5 mb-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]">
                      Edit
                    </CommandItem>
                    <CommandSeparator />
                    <CommandItem value="remove" @click="handleModelOperation('remove', model?.id)"
                      class="px-2 py-1.5 mb-1 mt-1 text-[#F9FAFB] cursor-pointer [&:hover]:!bg-[#6D28D9] [&:hover]:!text-[#F9FAFB]">
                      Remove
                    </CommandItem>
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </div>
      </div>
      <div class="flex flex-row gap-4 items-start justify-start shrink-0 relative">
        <div
          class="text-text-text-muted-foreground text-left font-['Inter-Regular',_sans-serif] text-xs leading-5 font-normal relative">
          First Published: {{ currentVersion?.created_at }}
        </div>
        <div
          class="text-text-text-muted-foreground text-left font-['Inter-Regular',_sans-serif] text-xs leading-5 font-normal relative">
          Last Updated: {{ currentVersion?.updated_at }}
        </div>
      </div>
    </div>
    <div class="flex flex-row gap-8  items-start justify-start self-stretch flex-1 relative">
      <div class="flex flex-col gap-4 items-start justify-start  relative min-w-[620px] w-[65%]   overflow-hidden ">
        <div class="w-full min-h-[80vh]">
          <MdPreview v-if="currentVersion?.intro" id="previewRef" :modelValue="currentVersion?.intro"
            :noImgZoomIn="true" :preview="true" theme="dark" class="bg-[#353535] w-full min-h-[80vh]" />
          <div v-else class="w-full h-[80vh] bg-[#353535] rounded-tl-lg rounded-tr-lg">
            <div class="flex justify-center items-center h-full">
              <div
                class="text-text-text-muted-foreground text-left font-['Inter-Regular',_sans-serif] text-xs leading-5 font-normal relative">
                No introduction yet
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="flex flex-col gap-6 items-start justify-start w-[40%] relative">
        <div class="pb-8 flex flex-col gap-6 items-start justify-start shrink-0   h-[97px] relative">
          <div class="flex flex-row gap-2 items-center justify-start shrink-0 relative">
            <Avatar>
              <AvatarImage src="https://github.com/radix-vue.png" alt="@radix-vue" />
              <AvatarFallback>{{ model?.user_name.slice(0, 2) }}</AvatarFallback>
            </Avatar>
            {{ model?.user_name }}
          </div>
          <div class="flex flex-row gap-1.5 items-start justify-start self-stretch shrink-0 relative">
            <Button variant="default" v-if="modelStoreInstance.mode === 'publicity'"
              class="w-[124px] flex h-9 px-3 py-2 justify-center items-center gap-2 flex-1 rounded-md bg-[#6D28D9]"
              @click="handleFork" :disabled="currentVersion?.forked">
              {{ currentVersion?.forked ? 'Forked' : 'Fork' }}
            </Button>
            <Button @click="handleApply"
              class="flex w-[170px] px-8 py-2 justify-center items-center gap-2 bg-[#F43F5E] hover:bg-[#F43F5E]/90 rounded-[6px]">
              <svg xmlns="http://www.w3.org/2000/svg" width="17" height="16" viewBox="0 0 17 16" fill="none">
                <path
                  d="M6.49988 7.9999L7.83322 9.33324L10.4999 6.66657M3.06655 5.74657C2.96925 5.30825 2.98419 4.85246 3.10999 4.42146C3.23579 3.99046 3.46838 3.5982 3.7862 3.28105C4.10401 2.9639 4.49676 2.73213 4.92802 2.60723C5.35929 2.48233 5.81511 2.46835 6.25322 2.56657C6.49436 2.18944 6.82655 1.87907 7.21919 1.66409C7.61182 1.44911 8.05225 1.33643 8.49988 1.33643C8.94752 1.33643 9.38795 1.44911 9.78058 1.66409C10.1732 1.87907 10.5054 2.18944 10.7466 2.56657C11.1853 2.46792 11.6419 2.48184 12.0739 2.60704C12.5058 2.73225 12.8991 2.96466 13.2171 3.28267C13.5351 3.60068 13.7675 3.99395 13.8927 4.4259C14.0179 4.85786 14.0319 5.31446 13.9332 5.75324C14.3104 5.99437 14.6207 6.32657 14.8357 6.7192C15.0507 7.11183 15.1634 7.55227 15.1634 7.9999C15.1634 8.44754 15.0507 8.88797 14.8357 9.2806C14.6207 9.67323 14.3104 10.0054 13.9332 10.2466C14.0314 10.6847 14.0175 11.1405 13.8926 11.5718C13.7677 12.003 13.5359 12.3958 13.2187 12.7136C12.9016 13.0314 12.5093 13.264 12.0783 13.3898C11.6473 13.5156 11.1915 13.5305 10.7532 13.4332C10.5124 13.8118 10.1799 14.1235 9.78663 14.3394C9.39333 14.5554 8.9519 14.6686 8.50322 14.6686C8.05453 14.6686 7.6131 14.5554 7.2198 14.3394C6.8265 14.1235 6.49404 13.8118 6.25322 13.4332C5.81511 13.5315 5.35929 13.5175 4.92802 13.3926C4.49676 13.2677 4.10401 13.0359 3.7862 12.7188C3.46838 12.4016 3.23579 12.0093 3.10999 11.5783C2.98419 11.1473 2.96925 10.6916 3.06655 10.2532C2.68652 10.0127 2.37349 9.68002 2.15658 9.28605C1.93967 8.89207 1.82593 8.44964 1.82593 7.9999C1.82593 7.55016 1.93967 7.10773 2.15658 6.71376C2.37349 6.31979 2.68652 5.98707 3.06655 5.74657Z"
                  stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
              </svg>Apply</Button>
          </div>
        </div>
        <div
          class="rounded-[6px] border-solid border-[rgba(78,78,78,0.50)] border flex flex-col gap-0 items-start justify-start self-stretch shrink-0 relative text-[#F9FAFB] font-inter text-sm font-medium leading-5">
          <div className="flex w-full text-gray-300 text-sm">
            <div className="w-[100px] bg-[#4E4E4E80] p-4   border-b border-[rgba(78,78,78,0.50)]">
              Type</div>
            <div className="flex-1 p-4 border-b text-sm border-[rgba(78,78,78,0.50)]">
              <span
                :class="`${model?.type} inline-flex px-[10px] py-[2px] items-start gap-[10px] rounded-[9999px] relative overflow-hidden`">
                {{ model?.type }}
              </span>
            </div>
          </div>
          <div className="flex w-full">
            <div
              className="w-[100px] bg-[#4E4E4E80] p-4 text-sm  border-b border-[rgba(78,78,78,0.50)] whitespace-nowrap">
              Base Model</div>
            <div className="flex-1 p-4 border-b  border-[rgba(78,78,78,0.50)]">
              {{ currentVersion?.base_model }}
            </div>
          </div>
          <div className="flex w-full">
            <div className="w-[100px] bg-[#4E4E4E80] p-4  border-b border-[rgba(78,78,78,0.50)]">
              Published</div>
            <div className="flex-1 p-4 border-b border-[rgba(78,78,78,0.50)]">
              {{ currentVersion?.created_at }}
            </div>
          </div>
          <div className="flex w-full">
            <div className="w-[100px] bg-[#4E4E4E80] p-4  border-b border-[rgba(78,78,78,0.50)]">
              Hash</div>
            <div className="flex-1 p-4 border-b border-[rgba(78,78,78,0.50)] flex items-center gap-2">
              <span>
                {{ currentVersion?.sign ? sliceString(currentVersion?.sign, 15) : '' }}
              </span>
              <svg xmlns="http://www.w3.org/2000/svg" v-if="currentVersion?.sign" width="16" height="16"
                viewBox="0 0 16 16" fill="none" class="cursor-pointer hover:opacity-80"
                @click="handleCopy(currentVersion?.sign || '')">
                <g clip-path="url(#clip0_315_3710)">
                  <path
                    d="M2.66659 10.6666C1.93325 10.6666 1.33325 10.0666 1.33325 9.33325V2.66659C1.33325 1.93325 1.93325 1.33325 2.66659 1.33325H9.33325C10.0666 1.33325 10.6666 1.93325 10.6666 2.66659M6.66658 5.33325H13.3333C14.0696 5.33325 14.6666 5.93021 14.6666 6.66658V13.3333C14.6666 14.0696 14.0696 14.6666 13.3333 14.6666H6.66658C5.93021 14.6666 5.33325 14.0696 5.33325 13.3333V6.66658C5.33325 5.93021 5.93021 5.33325 6.66658 5.33325Z"
                    stroke="#9CA3AF" stroke-linecap="round" stroke-linejoin="round" />
                </g>
                <defs>
                  <clipPath id="clip0_315_3710">
                    <rect width="16" height="16" fill="white" />
                  </clipPath>
                </defs>
              </svg>
            </div>
          </div>
          <div className="flex w-full">
            <div className="w-[100px] bg-[#4E4E4E80] p-4 text-gray-300   border-b border-[rgba(78,78,78,0.50)]">
              Stats</div>
            <div className="flex-1 p-4 border-b border-[rgba(78,78,78,0.50)] flex flex-row gap-2">
              <div
                class="bg-[#6D28D933] rounded-radius-rounded-xl pr-1.5 pl-1.5 flex flex-row gap-1 items-center justify-center shrink-0 min-w-[40px] relative overflow-hidden">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M3.33325 2L12.6666 8L3.33325 14V2Z" stroke="#F9FAFB" stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
                <div
                  class="text-text-text-foreground text-left font-['Inter-Regular',_sans-serif] text-sm leading-5 font-normal relative flex-1">
                  {{ formatNumber(currentVersion?.counter?.used_count) }}
                </div>
              </div>
              <div
                class="bg-[#6D28D933] rounded-radius-rounded-xl pr-1.5 pl-1.5 flex flex-row gap-1 items-center justify-center shrink-0 min-w-[40px] relative overflow-hidden">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path
                    d="M7.99992 1.33325L10.0599 5.50659L14.6666 6.17992L11.3333 9.42659L12.1199 14.0133L7.99992 11.8466L3.87992 14.0133L4.66659 9.42659L1.33325 6.17992L5.93992 5.50659L7.99992 1.33325Z"
                    stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div
                  class="text-text-text-foreground text-left font-['Inter-Regular',_sans-serif] text-sm leading-5 font-normal relative flex-1">
                  {{ formatNumber(currentVersion?.counter?.forked_count) }}
                </div>
              </div>
              <div
                class="bg-[#6D28D933] rounded-radius-rounded-xl pr-1.5 pl-1.5 flex flex-row gap-1 items-center justify-center shrink-0 min-w-[40px] relative overflow-hidden">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <g clip-path="url(#clip0_315_3742)">
                    <path
                      d="M4.66659 6.66658V14.6666M9.99992 3.91992L9.33325 6.66658H13.2199C13.4269 6.66658 13.6311 6.71478 13.8162 6.80735C14.0013 6.89992 14.1624 7.03432 14.2866 7.19992C14.4108 7.36551 14.4947 7.55775 14.5317 7.7614C14.5688 7.96506 14.5579 8.17454 14.4999 8.37325L12.9466 13.7066C12.8658 13.9835 12.6974 14.2268 12.4666 14.3999C12.2358 14.573 11.9551 14.6666 11.6666 14.6666H2.66659C2.31296 14.6666 1.97382 14.5261 1.72378 14.2761C1.47373 14.026 1.33325 13.6869 1.33325 13.3333V7.99992C1.33325 7.6463 1.47373 7.30716 1.72378 7.05711C1.97382 6.80706 2.31296 6.66658 2.66659 6.66658H4.50659C4.75464 6.66645 4.99774 6.59713 5.20856 6.4664C5.41937 6.33567 5.58953 6.14873 5.69992 5.92659L7.99992 1.33325C8.3143 1.33715 8.62374 1.41203 8.90512 1.55232C9.1865 1.6926 9.43254 1.89466 9.62486 2.14339C9.81717 2.39212 9.9508 2.68109 10.0157 2.98872C10.0807 3.29635 10.0753 3.61468 9.99992 3.91992Z"
                      stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
                  </g>
                  <defs>
                    <clipPath id="clip0_315_3742">
                      <rect width="16" height="16" fill="white" />
                    </clipPath>
                  </defs>
                </svg>
                <div
                  class="text-text-text-foreground text-left font-['Inter-Regular',_sans-serif] text-sm leading-5 font-normal relative flex-1">
                  {{ formatNumber(currentVersion?.counter?.liked_count) }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div
          class="rounded-md border-solid border-[#4e4e4e] border flex flex-col gap-0 items-start justify-start self-stretch shrink-0 relative">
          <div
            class="bg-[#424242] rounded-md flex items-center justify-start self-stretch shrink-0 relative h-[44px] pl-2">
            File
          </div>
          <div
            class="flex px-[8px] py-4 items-center self-stretch text-[#F9FAFB] font-inter text-xs font-medium leading-5">
            {{ currentVersion?.file_name ? sliceString(currentVersion?.file_name, 20) : '' }} ({{
              formatSize(currentVersion?.file_size) }})
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.md-editor-dark {
  @apply bg-[#353535] text-[#F9FAFB] text-sm;
}

.md-editor-dark {
  @apply bg-[#353535] text-[#F9FAFB];
}

:deep(.md-editor-preview-wrapper) {
  @apply text-[#F9FAFB];
}

:deep(.md-editor-preview) {
  @apply text-[#F9FAFB];

  p,
  li,
  table {
    @apply text-[#F9FAFB];
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    @apply text-[#F9FAFB];
  }

  code {
    @apply text-[#F9FAFB] bg-[#424242];
  }

  blockquote {
    @apply text-[#F9FAFB] border-l-4 border-[#6b7280];
  }
}



:deep([role="tablist"]) {
  display: inline-flex;
  min-width: min-content;
}

:deep([data-radix-scroll-area-viewport]) {
  width: 100%;
}

.Checkpoint {
  background: rgba(109, 40, 217, 0.40);
}

.LoRA {
  background: rgba(244, 63, 94, 0.40);
}

.Controlnet {
  background: rgba(255, 255, 255, 0.40);
}

.VAE {
  background: rgba(234, 179, 8, 0.40);
}

.Upscaler {
  background: rgba(69, 244, 63, 0.40);
}

.Embeddings {
  background: rgba(0, 26, 255, 0.40);
}

.Workflow {
  background: rgba(0, 178, 255, 0.40);
}
</style>
