<template>
  <!-- <btnMenu :show_cases="show_cases" buttonText="Examples" icon="book-open" :isJson="true">
    <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
      <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 16.008V7.99a1.98 1.98 0 0 0-1-1.717l-7-4.008a2.02 2.02 0 0 0-2 0L4 6.273c-.619.355-1 1.01-1 1.718v8.018c0 .709.381 1.363 1 1.717l7 4.008a2.02 2.02 0 0 0 2 0l7-4.008c.619-.355 1-1.01 1-1.718M12 22V12m0 0l8.73-5.04m-17.46 0L12 12" />
    </svg>
  </btnMenu> -->
  <!-- <Form v-slot="{ submitForm }" as="" :validation-schema="formSchema"> -->
    <div @click="showDialog = true" class="flex items-center hover:bg-[#4A238E] cursor-pointer relative px-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
        <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M21 16.008V7.99a1.98 1.98 0 0 0-1-1.717l-7-4.008a2.02 2.02 0 0 0-2 0L4 6.273c-.619.355-1 1.01-1 1.718v8.018c0 .709.381 1.363 1 1.717l7 4.008a2.02 2.02 0 0 0 2 0l7-4.008c.619-.355 1-1.01 1-1.718M12 22V12m0 0l8.73-5.04m-17.46 0L12 12" />
      </svg>
      <span class="block leading h-full leading-8 text-sm">Examples</span>
    </div>
    <!-- <Dialog v-model:open="showDialog" closeOnOverlayClick="false">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Publish a Model</DialogTitle>
        </DialogHeader>


        <FormField name="ModelName" v-slot="{ field, meta }">
          <FormItem>
            <FormLabel>Model Name</FormLabel>
            <FormControl>
              <Input type="text" placeholder="shadcn" v-model:model-value="formData.modelName" v-bind="field" />
            </FormControl>
            <FormDescription>This is your public display name.</FormDescription>
            <FormMessage v-if="meta.touched && meta.error">{{ meta.error }}</FormMessage>
          </FormItem>
        </FormField>

        <FormField name="modelType" v-slot="{ field, meta }">
          <FormItem>
            <FormLabel>Model Type</FormLabel>
            <FormControl>
              <Select v-bind="field" v-model:model-value="formData.modelType">
                <SelectTrigger>
                  <SelectValue placeholder="Select a model type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectItem value="apple">Apple</SelectItem>
                    <SelectItem value="apple2">Apple2</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </FormControl>
            <FormDescription>This is your public display name.</FormDescription>
            <FormMessage v-if="meta.touched && meta.error">{{ meta.error }}</FormMessage>
          </FormItem>
        </FormField>

        <Button class="w-full mt-3" @click="nextStep">Next Step</Button>

      </DialogContent>
    </Dialog> -->
    <!-- <Dialog v-model:open="showDialog" closeOnOverlayClick="false">

    </Dialog> -->
  <!-- </Form> -->
</template>
<script setup lang="ts">
import { ref } from 'vue'
// import {
//   Dialog,
//   DialogContent,
//   // DialogDescription,
//   // DialogFooter,
//   DialogHeader,
//   DialogTitle,
// } from '@/components/ui/dialog'
// import {
//   Form,
//   FormControl,
//   FormDescription,
//   FormField,
//   FormItem,
//   FormLabel,
//   FormMessage,
// } from '@/components/ui/form'
// import {
//   Select,
//   SelectContent,
//   SelectGroup,
//   SelectItem,
//   // SelectLabel,
//   SelectTrigger,
//   SelectValue,
// } from '@/components/ui/select'
// import * as z from 'zod'
// import { toTypedSchema } from '@vee-validate/zod'
// import { toast } from '@/components/ui/toast'
// import { Input } from '@/components/ui/input'
// // import { h } from 'vue'
// import { Button } from '@/components/ui/button'
import { createModels } from '@/api/model'
const showDialog = ref(false)
// const formData = ref({
//   modelName: '',
//   modelType: '',
// })
// const formSchema = toTypedSchema(z.object({
//   ModelName: z.string().min(2).max(50),
//   modelType: z.string(),
// }))


// function nextStep() {

// }
createModels
</script>
<style scoped></style>
