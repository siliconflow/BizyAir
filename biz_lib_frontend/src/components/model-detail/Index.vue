<script setup lang="ts">
import {
  Tabs,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { ref, onMounted } from 'vue'
import Vditor from 'vditor'

import { Model, ModelVersion } from '@/types/model'
import { model_detail } from '@/api/model'

const previewRef = ref<HTMLDivElement | null>(null)
const model = ref<Model>()
const currentVerssion = ref<ModelVersion>()

const previewContent = async (content: string) => {
  if (previewRef.value) {
    if (!content) {
      previewRef.value.innerHTML = '<span>No content available</span>'
      return
    }
    const html = await Vditor.md2html(content, { mode: 'dark' })
    previewRef.value.innerHTML = html
  }
}
const props = defineProps<{
  modelId: string,
  mode: string
}>()

const getData = async () => {
  const res = await model_detail({ id: props.modelId, source: props.mode })
  console.log('[res]', res)
  model.value = res.data
  if (model.value?.versions && model.value?.versions.length > 0) {
    currentVerssion.value = model.value.versions?.[0]
    previewContent(currentVerssion.value.intro)
  }
}

onMounted(() => {
  getData()
})

const handleTabChange = (value: number) => {
  const version = model.value?.versions?.find(v => v.id === value)
  if (version) {
    currentVerssion.value = version
    previewContent(version.intro)
  }
}

</script>

<template>
  <div v-if="model"
    class="bg-[#353535] rounded-radius-rounded-lg border-solid border-border-border-toast-destructive border p-6 flex flex-col gap-4 items-start justify-start  min-w-[1000px] h-screen mb-[100px] relative"
    style="box-shadow: 0px 20px 40px 0px rgba(0, 0, 0, 0.25)">
    <div class="flex flex-col gap-1.5 items-start justify-start self-stretch shrink-0 relative">
      <div class="flex flex-row gap-2 items-center justify-start self-stretch shrink-0 relative">
        <div
          class="text-text-text-foreground text-left font-['Inter-SemiBold',_sans-serif] text-lg leading-[18px] font-semibold relative"
          style="letter-spacing: -0.025em">
          {{ model?.name }}
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
              {{ model?.counter?.forked_count || 0 }}
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
            {{ model?.counter?.liked_count || 0 }}
          </div>
        </div>
      </div>
      <div class="flex flex-row gap-1 items-center justify-start self-stretch shrink-0 relative">
        <div
          class="bg-[#4e4e4e] rounded-lg p-1 flex flex-row gap-4 items-start justify-start self-stretch shrink-0 relative">
          <Tabs :defaultValue="currentVerssion?.id" :value="currentVerssion?.id">
            <TabsList class="grid w-full grid-cols-3 h-12 bg-[#4E4E4E] text-sm">
              <TabsTrigger v-for="version in model?.versions" :value="version.id" @click="handleTabChange(version.id)"
                class="text-sm text-white data-[state=active]:bg-[#9CA3AF] data-[state=active]:text-white h-10 px-3 py-2 ">
                {{ version.version }}
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        <div
          class="text-text-text-muted-foreground text-left font-['Inter-Regular',_sans-serif] text-xs leading-5 font-normal relative flex-1">
        </div>
        <div class="flex gap-8">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <g clip-path="url(#clip0_440_1289)">
              <path
                d="M4.66659 6.66658V14.6666M9.99992 3.91992L9.33325 6.66658H13.2199C13.4269 6.66658 13.6311 6.71478 13.8162 6.80735C14.0013 6.89992 14.1624 7.03432 14.2866 7.19992C14.4108 7.36551 14.4947 7.55775 14.5317 7.7614C14.5688 7.96506 14.5579 8.17454 14.4999 8.37325L12.9466 13.7066C12.8658 13.9835 12.6974 14.2268 12.4666 14.3999C12.2358 14.573 11.9551 14.6666 11.6666 14.6666H2.66659C2.31296 14.6666 1.97382 14.5261 1.72378 14.2761C1.47373 14.026 1.33325 13.6869 1.33325 13.3333V7.99992C1.33325 7.6463 1.47373 7.30716 1.72378 7.05711C1.97382 6.80706 2.31296 6.66658 2.66659 6.66658H4.50659C4.75464 6.66645 4.99774 6.59713 5.20856 6.4664C5.41937 6.33567 5.58953 6.14873 5.69992 5.92659L7.99992 1.33325C8.3143 1.33715 8.62374 1.41203 8.90512 1.55232C9.1865 1.6926 9.43254 1.89466 9.62486 2.14339C9.81717 2.39212 9.9508 2.68109 10.0157 2.98872C10.0807 3.29635 10.0753 3.61468 9.99992 3.91992Z"
                stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
            </g>
            <defs>
              <clipPath id="clip0_440_1289">
                <rect width="16" height="16" fill="white" />
              </clipPath>
            </defs>
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
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
      </div>
      <div class="flex flex-row gap-4 items-start justify-start shrink-0 relative">
        <div
          class="text-text-text-muted-foreground text-left font-['Inter-Regular',_sans-serif] text-xs leading-5 font-normal relative">
          First Published: {{ currentVerssion?.created_at }}
        </div>
        <div
          class="text-text-text-muted-foreground text-left font-['Inter-Regular',_sans-serif] text-xs leading-5 font-normal relative">
          Last Updated: {{ currentVerssion?.updated_at }}
        </div>
      </div>
    </div>
    <div class="flex flex-row gap-8 items-start justify-start self-stretch flex-1 relative">
      <div class="flex flex-col gap-4 items-start justify-start  relative min-w-[620px] w-[65%]">
        <div ref="previewRef"></div>
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
            <Button variant="default"
              class="w-[124px] flex h-9 px-3 py-2 justify-center items-center gap-2 flex-1 rounded-md bg-[#6D28D9]">Fork</Button>
            <Button
              class="flex w-[170px] px-8 py-2 justify-center items-center gap-2 bg-[#F43F5E] hover:bg-[#F43F5E]/90 rounded-[6px]">
              <svg xmlns="http://www.w3.org/2000/svg" width="17" height="16" viewBox="0 0 17 16" fill="none">
                <path
                  d="M6.49988 7.9999L7.83322 9.33324L10.4999 6.66657M3.06655 5.74657C2.96925 5.30825 2.98419 4.85246 3.10999 4.42146C3.23579 3.99046 3.46838 3.5982 3.7862 3.28105C4.10401 2.9639 4.49676 2.73213 4.92802 2.60723C5.35929 2.48233 5.81511 2.46835 6.25322 2.56657C6.49436 2.18944 6.82655 1.87907 7.21919 1.66409C7.61182 1.44911 8.05225 1.33643 8.49988 1.33643C8.94752 1.33643 9.38795 1.44911 9.78058 1.66409C10.1732 1.87907 10.5054 2.18944 10.7466 2.56657C11.1853 2.46792 11.6419 2.48184 12.0739 2.60704C12.5058 2.73225 12.8991 2.96466 13.2171 3.28267C13.5351 3.60068 13.7675 3.99395 13.8927 4.4259C14.0179 4.85786 14.0319 5.31446 13.9332 5.75324C14.3104 5.99437 14.6207 6.32657 14.8357 6.7192C15.0507 7.11183 15.1634 7.55227 15.1634 7.9999C15.1634 8.44754 15.0507 8.88797 14.8357 9.2806C14.6207 9.67323 14.3104 10.0054 13.9332 10.2466C14.0314 10.6847 14.0175 11.1405 13.8926 11.5718C13.7677 12.003 13.5359 12.3958 13.2187 12.7136C12.9016 13.0314 12.5093 13.264 12.0783 13.3898C11.6473 13.5156 11.1915 13.5305 10.7532 13.4332C10.5124 13.8118 10.1799 14.1235 9.78663 14.3394C9.39333 14.5554 8.9519 14.6686 8.50322 14.6686C8.05453 14.6686 7.6131 14.5554 7.2198 14.3394C6.8265 14.1235 6.49404 13.8118 6.25322 13.4332C5.81511 13.5315 5.35929 13.5175 4.92802 13.3926C4.49676 13.2677 4.10401 13.0359 3.7862 12.7188C3.46838 12.4016 3.23579 12.0093 3.10999 11.5783C2.98419 11.1473 2.96925 10.6916 3.06655 10.2532C2.68652 10.0127 2.37349 9.68002 2.15658 9.28605C1.93967 8.89207 1.82593 8.44964 1.82593 7.9999C1.82593 7.55016 1.93967 7.10773 2.15658 6.71376C2.37349 6.31979 2.68652 5.98707 3.06655 5.74657Z"
                  stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
              </svg>Apply</Button>
          </div>
        </div>
        <div
          class="rounded-[6px] border-solid border-[rgba(78,78,78,0.50)] border  flex flex-col gap-0 items-start justify-start self-stretch shrink-0 relative">
          <div className="flex w-full text-gray-300 text-sm">
            <div className="w-[100px] bg-[#4E4E4E80] p-4   border-b border-[rgba(78,78,78,0.50)]">
              Type</div>
            <div className="flex-1 p-4 border-b text-sm border-[rgba(78,78,78,0.50)]">
              {{ model?.type }}
            </div>
          </div>
          <div className="flex w-full">
            <div className="w-[100px] bg-[#4E4E4E80] p-4 text-sm  border-b border-[rgba(78,78,78,0.50)]">
              Base Model</div>
            <div className="flex-1 p-4 border-b  border-[rgba(78,78,78,0.50)]">
              {{ currentVerssion?.base_model }}
            </div>
          </div>
          <div className="flex w-full">
            <div className="w-[100px] bg-[#4E4E4E80] p-4  border-b border-[rgba(78,78,78,0.50)]">
              Published</div>
            <div className="flex-1 p-4 border-b border-[rgba(78,78,78,0.50)]">
              {{ currentVerssion?.created_at }}
            </div>
          </div>
          <div className="flex w-full">
            <div className="w-[100px] bg-[#4E4E4E80] p-4    border-b border-[rgba(78,78,78,0.50)]">
              Hash</div>
            <div className="flex-1 p-4 border-b border-[rgba(78,78,78,0.50)] flex items-center gap-2">
              <span>{{ currentVerssion?.sign ? (currentVerssion.sign.length > 11 ? currentVerssion.sign.slice(0, 11) +
                '...' :
                currentVerssion.sign) : '' }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
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
            <div className="w-[100px] bg-[#4E4E4E80] p-4 text-gray-300 text-lg  border-b border-[rgba(78,78,78,0.50)]">
              Stats</div>
            <div className="flex-1 p-4 border-b border-[rgba(78,78,78,0.50)]">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3.33325 2L12.6666 8L3.33325 14V2Z" stroke="#F9FAFB" stroke-linecap="round"
                  stroke-linejoin="round" />
                {{ model?.counter?.forked_count || 0 }}

                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path
                    d="M7.99992 1.33325L10.0599 5.50659L14.6666 6.17992L11.3333 9.42659L12.1199 14.0133L7.99992 11.8466L3.87992 14.0133L4.66659 9.42659L1.33325 6.17992L5.93992 5.50659L7.99992 1.33325Z"
                    stroke="#F9FAFB" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                {{ model?.counter?.liked_count || 0 }}
              </svg>
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
            {{ currentVerssion?.file_name ? (currentVerssion.file_name.length > 20 ? currentVerssion.file_name.slice(0,
              20) + '...' :
              currentVerssion.file_name) : '' }} ({{ currentVerssion?.file_size }}G)
          </div>
        </div>
      </div>
    </div>

  </div>
</template>


<style scoped></style>
