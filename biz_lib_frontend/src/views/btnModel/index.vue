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
    <v-dialog v-model:open="showDialog">
      <template #title>Publish a Model</template>
      <FormField name="ModelName" >
        <FormItem>
          <FormLabel>Model Name</FormLabel>
          <FormControl>
            <Input type="text" placeholder="shadcn" v-model:model-value="formData.name" />
          </FormControl>
        </FormItem>
      </FormField>

      <FormField name="modelType">
        <FormItem>
          <FormLabel>Model Type</FormLabel>
          <FormControl>
            <v-select v-model:model-value="formData.type" placeholder="Select Model Type">
              <SelectItem v-for="(e, i) in typeLis" :key="i" :value="e.value">{{ e.label }}</SelectItem>
            </v-select>
          </FormControl>
        </FormItem>
      </FormField>
      <Button class="w-full mt-3" @click="nextStep">Next Step</Button>
    </v-dialog>
    <v-dialog v-model:open="showDialogVersion">

      <template #title>{{ formData.name }}</template>
      <p>Add a Version</p>
      <div v-for="(e, i) in formData.versions" :key="i">
        <FormField name="ModelName">
          <FormItem>
            <FormLabel>Version Name</FormLabel>
            <FormControl>
              <Input type="text" placeholder="shadcn" v-model:model-value="e.version" />
            </FormControl>
          </FormItem>

          <FormItem>
            <FormLabel>Base Model</FormLabel>
            <FormControl>
              <v-select v-model:model-value="e.base_model" placeholder="Select Base Model">
                <SelectItem v-for="(e, i) in baseTypeLis" :key="i" :value="e.value">{{ e.label }}</SelectItem>
              </v-select>
            </FormControl>
          </FormItem>

          <FormItem>
            <FormLabel>Intro</FormLabel>
            <FormControl>
              <Textarea type="text" placeholder="shadcn" v-model:model-value="e.intro" />
            </FormControl>
          </FormItem>

          <FormItem>
            <div class="flex items-center space-x-2 mt-2">
              <Switch id="airplane-mode" @update:checked="(val) => {handleChange(val, i)}" />
              <Label for="airplane-mode">Publicly Visible</Label>
            </div>
          </FormItem>

          <FormItem>
            <FormLabel>File Path</FormLabel>
            <FormControl>
              <Input type="text" @change="checkFile(e.filePath, i)" placeholder="shadcn" v-model:model-value="e.filePath" />
            </FormControl>
          </FormItem>
        </FormField>
      </div>

      <Button :disabled="disabledSubmit" icon="loadding" class="w-full mt-3" @click="nextStep2">Next Step</Button>
    </v-dialog>

  <!-- </Form> -->
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  // Form,
  FormControl,
  // FormDescription,
  FormField,
  FormItem,
  FormLabel,
  // FormMessage,
} from '@/components/ui/form'
import { SelectItem } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

// import * as z from 'zod'
// import { toTypedSchema } from '@vee-validate/zod'
// import { toast } from '@/components/ui/toast'
import { Input } from '@/components/ui/input'
// import { h } from 'vue'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import vDialog from '@/components/modules/vDialog.vue'
import vSelect from '@/components/modules/vSelect.vue'
import { useStatusStore} from '@/stores/userStatus'
import { modelStore } from '@/stores/modelStatus'

import { create_models, checkLocalFile, submitUpload, model_types, base_model_types, put_model } from '@/api/model'
import { onMounted } from 'vue'



const statusStore = useStatusStore();
const modelStoreObject = modelStore();
const showDialog = ref(false);
const showDialogVersion = ref(false);
const disabledSubmit = ref(false);
const versionIndex = ref(0);
const typeLis = ref([{value: '', label: ''}]);
const baseTypeLis = ref([{value: '', label: ''}]);
const formData = ref({...modelStoreObject.modelDetail});
// const formSchema = toTypedSchema(z.object({
//   ModelName: z.string().min(2).max(50),
//   modelType: z.string(),
// }));

function handleChange(val: any, index: number) {
  formData.value.versions[index].public = val
}
async function checkFile (val: string, index: number) {
  const res = await checkLocalFile({ absolute_path: val })
  console.log(res)
  if (res.data.upload_id) {
    disabledSubmit.value = true
    await submitUpload({ upload_id: res.data.upload_id })
    disabledSubmit.value = false
  }
  versionIndex.value = index
}
function nextStep() {
  showDialog.value = false
  showDialogVersion.value = true
}

function nextStep2() {
  console.log(formData.value)

  if (formData.value.id) {
    put_model(formData.value)
  } else {
    create_models(formData.value)
  }
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
onMounted(async () => {
  const mt = await model_types()
  typeLis.value = mt.data
  const bmt = await base_model_types()
  baseTypeLis.value = bmt.data
})
</script>
<style scoped></style>
