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
          <Input type="text" placeholder="shadcn" v-model:model-value="formData.name" />
        </v-item>
        <v-item label="Model Name">
          <v-select v-model:model-value="formData.type" placeholder="Select Model Type">
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
          <v-accordion-trigger class=" justify-between">
            <span v-if="acActiveIndex !== `${i}` && e.version">{{ e.version }}</span>
            <span v-else>Add Version</span>
            <BadgeMinus class="w-4 h-4" #icon @click.capture.stop="delVersion(i)" />
          </v-accordion-trigger>
          <AccordionContent>
            <v-item label="Version Name">
              <Input type="text" placeholder="shadcn" v-model:model-value="e.version" />
            </v-item>
            <v-item label="Base Model">
              <v-select v-model:model-value="e.base_model" placeholder="Select Base Model">
                <SelectItem v-for="(e, i) in baseTypeLis" :key="i" :value="e.value">{{ e.label }}</SelectItem>
              </v-select>
            </v-item>
            <v-item label="Intro">
              <!-- <Markdown editorId="veditor" @update:modelValue="handleMarkdownChange" /> -->
              <Markdown :editorId="`myeditor${i}`" @update:modelValue="handleMarkdownChange" @isUploading="handleIsUploading" />
              <!-- <Textarea type="text" placeholder="shadcn" v-model:model-value="e.intro" /> -->
            </v-item>
            <v-item label="">
              <div class="flex items-center space-x-2 mt-2">
                <Switch id="airplane-mode" @update:checked="(val) => {handleChange(val, i)}" />
                <Label for="airplane-mode">Publicly Visible</Label>
              </div>
            </v-item>
            <v-item label="File Path">
              <Input type="text" @change="checkFile(e.filePath, i)" placeholder="shadcn" v-model:model-value="e.filePath" />
            </v-item>
            <Button class="w-full mt-3" @click="nextStep">Next Step</Button>
          </AccordionContent>
        </AccordionItem>

      </Accordion>
      <template #foot>
        <div class="bg-[#353535] px-6 w-full h-14 rounded-tl-lg rounded-tr-lg custom-shadow border-t-[1px] flex justify-between items-center -mt-4">
          <Button type="button" class="" @click="nextStep">Add Version</Button>
          <Button class="" @click="acActiveIndex = '-1'">Close All</Button>
        </div>
      </template>
    </v-dialog>


</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { Accordion, AccordionContent, AccordionItem } from '@/components/ui/accordion'
import { SelectItem } from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
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

function handleChange(val: any, index: number) {
  if (formData.value.versions) {
    formData.value.versions[index].public = val;
  }
}
async function checkFile(val: string, index: number) {
  const res = await checkLocalFile({ absolute_path: val })
  console.log(res)
  if (res.data.upload_id) {
    disabledSubmit.value = true
    await submitUpload({ upload_id: res.data.upload_id })
    disabledSubmit.value = false
  }
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
  tempData.versions = tempData.versions || []
  tempData.versions.splice(index, 1)
  modelStoreObject.setModelDetail(tempData)
  if (tempData.versions.length == 1) {
    acActiveIndex.value = '0'
  }
  if (tempData.versions.length == 0) {
    modelBox.value = true
  }
}
function nextStep() {
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

function nextStep2() {
  console.log(formData.value)

  if (formData.value.id) {
    put_model(formData.value)
  } else {
    create_models(formData.value)
  }
}
nextStep2


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
  console.log(val)
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
  console.log(val)
  if (!val) {
    modelStoreObject.clearModelDetail()
    modelBox.value = true
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
