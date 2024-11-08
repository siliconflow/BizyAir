<template>
  <!-- <btnMenu :show_cases="show_cases" buttonText="Examples" icon="book-open" :isJson="true">
    <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
      <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 16.008V7.99a1.98 1.98 0 0 0-1-1.717l-7-4.008a2.02 2.02 0 0 0-2 0L4 6.273c-.619.355-1 1.01-1 1.718v8.018c0 .709.381 1.363 1 1.717l7 4.008a2.02 2.02 0 0 0 2 0l7-4.008c.619-.355 1-1.01 1-1.718M12 22V12m0 0l8.73-5.04m-17.46 0L12 12" />
    </svg>
  </btnMenu> -->
  <!-- <Form as="" :validation-schema="formSchema"> -->
    <div @click="showDialog = true" class="flex items-center hover:bg-[#4A238E] cursor-pointer relative px-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
        <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M21 16.008V7.99a1.98 1.98 0 0 0-1-1.717l-7-4.008a2.02 2.02 0 0 0-2 0L4 6.273c-.619.355-1 1.01-1 1.718v8.018c0 .709.381 1.363 1 1.717l7 4.008a2.02 2.02 0 0 0 2 0l7-4.008c.619-.355 1-1.01 1-1.718M12 22V12m0 0l8.73-5.04m-17.46 0L12 12" />
      </svg>
      <span class="block leading h-full leading-8 text-sm">Publish</span>
    </div>
    <v-dialog
      v-model:open="showDialog"
      class="px-0 overflow-hidden pb-0"
      contentClass="custom-scrollbar max-h-[80vh] overflow-y-auto w-full rounded-tl-lg rounded-tr-lg custom-shadow">
      <template #title><span class="px-6" @click="acActiveIndex = '-1'; modelBox = true">Publish a Model</span></template>
      <div v-show="modelBox" class="px-6 pb-6">
        <v-item label="Model Name">
          <Input @change="formData.nameError = false" :class="{'border-red-500': formData.nameError}" type="text" placeholder="Enter Model Name" v-model:model-value="formData.name" />
        </v-item>
        <v-item label="Model Type">
          <v-select @update:open="formData.typeError = false" :class="{'border-red-500': formData.typeError}" v-model:model-value="formData.type" placeholder="Select Model Type">
            <SelectItem v-for="(e, i) in typeLis" :key="i" :value="e.value">{{ e.label }}</SelectItem>
          </v-select>
        </v-item>
        <Button class="w-full mt-3" @click="nextStep">Next Step</Button>
      </div>
      <Accordion
        type="single"
        collapsible
        default-value="0"
        class="w-full"
        @update:model-value="acActiveFn"
        v-model:model-value="acActiveIndex">
        <AccordionItem class="bg-[#353535] z-1 px-6 w-full rounded-tl-lg rounded-tr-lg custom-shadow border-t-[1px]" v-for="(e, i) in formData.versions" :key="i" :value="`${i}`">
          <v-accordion-trigger class="justify-between relative">
            <span v-if="acActiveIndex !== `${i}` && e.version">{{ e.version }}</span>
            <span v-else>Add Version</span>
            <BadgeMinus v-if="formData.versions.length !== 1" class="w-4 h-4" #icon @click.capture.stop="delVersion(i)" />
            <Progress v-if="e.progress && e.progress.value" :model-value="e.progress.value" class="absolute w-full bottom-0 left-0 h-1" />
          </v-accordion-trigger>
          <AccordionContent>
            <v-item label="Version Name">
              <Input @change="e.versionError = false" :class="{'border-red-500': e.versionError}" type="text" placeholder="" v-model:model-value="e.version" />
            </v-item>
            <v-item label="Base Model">
              <v-select @update:open="e.baseModelError = false" :class="{'border-red-500': e.baseModelError}" v-model:model-value="e.base_model" placeholder="Select Base Model">
                <SelectItem v-for="(e, i) in baseTypeLis" :key="i" :value="e.value">{{ e.label }}</SelectItem>
              </v-select>
            </v-item>
            <v-item label="Introduction">
              <Markdown :editorId="`myeditor${i}`" @update:modelValue="handleMarkdownChange" @isUploading="handleIsUploading" />
            </v-item>
            <v-item label="">
              <div class="flex items-center space-x-2 mt-2">
                <Switch id="airplane-mode" @update:checked="(val) => {handleChange(val, i)}" />
                <Label for="airplane-mode">Publicly Visible</Label>
              </div>
            </v-item>
            <v-item label="File Path">
              <Input :class="{'border-red-500': e.filePathError}" type="text" @change="checkFile(e.filePath, i)" placeholder="" v-model:model-value="e.filePath" />
            </v-item>
            <div v-if="e.progress && e.progress.value">
              <Progress  :model-value="e.progress.value" class="mt-4 h-3" />
              <p class="text-center mt-2">20% Uploaded</p>
            </div>
          </AccordionContent>
        </AccordionItem>

      </Accordion>
      <template #foot v-if="!modelBox">
        <div class="bg-[#353535] px-6 w-full h-14 rounded-tl-lg rounded-tr-lg custom-shadow border-t-[1px] flex justify-between items-center -mt-4">
          <Button variant="ghost" class="" @click="addVersions">Add Version</Button>
          <Button @click="submit">Publish</Button>
        </div>
      </template>
      <div v-if="showLayoutLoading" class="z-50 w-full h-full absolute left-0 top-0"></div>
    </v-dialog>


</template>
<script setup lang="ts">
import { toast } from 'vue-sonner'
import { ref, watch } from 'vue'
import { Accordion, AccordionContent, AccordionItem } from '@/components/ui/accordion'
import { SelectItem } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Progress } from '@/components/ui/progress'
import vDialog from '@/components/modules/vDialog.vue'
import vSelect from '@/components/modules/vSelect.vue'
import vItem from '@/components/modules/vItem.vue'
import vAccordionTrigger from '@/components/modules/vAccordionTrigger.vue'
import { useAlertDialog  } from '@/components/modules/vAlertDialog/index'

import { useStatusStore} from '@/stores/userStatus'
import { modelStore } from '@/stores/modelStatus'
import { Markdown } from '@/components/markdown'
import { create_models, checkLocalFile, submitUpload, model_types, base_model_types, put_model } from '@/api/model'
import { onMounted } from 'vue'
import { BadgeMinus  } from 'lucide-vue-next'


const statusStore = useStatusStore();
const modelStoreObject = modelStore();
const showDialog = ref(false);
const disabledSubmit = ref(false);
const modelBox = ref(true);
const versionIndex = ref(0);
const typeLis = ref([{ value: '', label: '' }]);
const baseTypeLis = ref([{ value: '', label: '' }]);
const formData = ref({ ...modelStoreObject.modelDetail });
const acActiveIndex = ref('0')
const showLayoutLoading = ref(false)

function handleChange(val: any, index: number) {
  if (formData.value.versions) {
    formData.value.versions[index].public = val;
  }
}
async function checkFile(val: string, index: number) {
  const res = await checkLocalFile({ absolute_path: val })
  formData.value.versions[index].file_upload_id = res.data.upload_id
  formData.value.versions[index].filePathError = false
  versionIndex.value = index
}
async function delVersion(index: number) {
  const res = await useAlertDialog({
    title: 'Are you sure you want to delete this version?',
    desc: 'This action cannot be undone.',
    cancel: 'No, Keep It',
    continue: 'Yes, Delete It',
  })
  if (!res) return
  const tempData = {...formData.value}
  if (acActiveIndex.value === `${tempData.versions.length - 1}`) {
    acActiveIndex.value = `${Number(acActiveIndex.value) - 1}`
  }
  tempData.versions = tempData.versions || []
  tempData.versions.splice(index, 1)
  modelStoreObject.setModelDetail(tempData)
  if (tempData.versions.length === 1) {
    acActiveIndex.value = '0'
  }
  if (tempData.versions.length === 0) {
    modelBox.value = true
  }
}
function addVersions() {
  const tempData = {...formData.value}
  tempData.versions = tempData.versions || []
  tempData.versions.push({
    version: '',
    base_model: '',
    intro: '',
    public: false,
    filePath: '',
    sign: '',
    path: ''
  })
  modelStoreObject.setModelDetail(tempData)
  modelBox.value = false
  acActiveIndex.value = `${tempData.versions.length - 1}`
}

function nextStep() {
  if(!formData.value.name) {
    toast.error('Please enter the model name')
    formData.value.nameError = true
    return
  }
  if(!formData.value.type) {
    toast.error('Please select the model type')
    formData.value.typeError = true
    return
  }
  if (formData.value.versions.length) {
    acActiveIndex.value = `${formData.value.versions.length - 1}`
    modelBox.value = false
  } else {
    addVersions()
  }
}

function verifyVersion() {
  const tempData = {...formData.value}
  tempData.versions = tempData.versions || []
  tempData.versions.forEach((e: any, i: number) => {
    if (!e.version) {
      e.versionError = true
      toast.error(`Please enter the version name for version ${i + 1}`)
    }
    if (!e.base_model) {
      e.baseModelError = true
    }
    if (!e.filePath) {
      e.filePathError = true
    }
  })
  for(let i = 0; i < tempData.versions.length; i++) {
    const e = tempData.versions[i]
    if (!e.version) {
      e.versionError = true
      toast.error(`Please enter the version name for version ${i + 1}`)
    }
    if (!e.base_model) {
      e.baseModelError = true
      toast.error(`Please select the base model for version ${i + 1}`)
    }
    if (!e.filePath) {
      e.filePathError = true
      toast.error(`Please enter the file path for version ${i + 1}`)
    }
    acActiveIndex.value = `${i}`
    console.log(i)
    break
  }
  // modelStoreObject.setModelDetail(tempData)
  return tempData.versions.every((e: any) => e.version && e.base_model && e.filePath)
}
function submit() {
  // showLayoutLoading.value = true
  if (!verifyVersion()) {
    // showLayoutLoading.value = false
    return
  }
  toast.error('You may be missing dependencies at the moment. For details, please refer to the ComfyUI logs.',{})
  // toast('Event has been created', {
  //   description: 'Sunday, December 03, 2023 at 9:00 AM',
  //   action: {
  //     label: 'Undo',
  //     onClick: () => console.log('Undo'),
  //   },

  // })
  console.log(formData.value)
  if (!formData.value.id) return
  submitUpload
  disabledSubmit
  // if (res.data.upload_id) {
  //   disabledSubmit.value = true
  //   await submitUpload({ upload_id: res.data.upload_id })
  //   disabledSubmit.value = false
  // }
  if (formData.value.id) {
    put_model(formData.value)
  } else {
    create_models(formData.value)
  }
}

const acActiveFn = () => {
  if (modelBox.value) {
    modelBox.value = false
  }
}
const handleMarkdownChange = (value: string) => {
  console.log('md content', value)
  formData.value.versions[versionIndex.value].intro = value
}
const handleIsUploading = (val: boolean) => {
  // disabledSubmit.value = val
  console.log(val)
}
watch(() => statusStore.socketMessage, (val: any) => {
  if (val.type == "status" && val.data.status == 'finish') {
    const i = versionIndex.value
    formData.value.versions[i].path = val.data.model_files[0].path
    formData.value.versions[i].sign = val.data.model_files[0].sign
  }
}, {
  deep: true
})
watch(() => modelStoreObject.modelDetail, (val: any) => {
  formData.value = val
}, {
  deep: true
})
watch(showDialog, (val: any) => {
  if (!val) {
    modelStoreObject.clearModelDetail()
    modelBox.value = true
    showLayoutLoading.value = false
  }
})
onMounted(async () => {
  const mt = await model_types()
  typeLis.value = mt.data
  const bmt = await base_model_types()
  baseTypeLis.value = bmt.data
})
</script>
<style scoped>
.custom-shadow {
  box-shadow: 0px -6px 20px 0px rgba(255, 255, 255, 0.10);
}
</style>
