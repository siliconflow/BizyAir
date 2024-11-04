<template>
  <div @click="showDialog = true" class="flex items-center hover:bg-[#4A238E] cursor-pointer relative px-3">
    <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
      <path fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
        d="m15.362 9.065l1.32 1.32c.995.995 1.345-.84 2.734-1.07c.466-.078.877-.236 1.053-.752c.156-.456-.021-.885-.574-1.438L18.5 5.731M7.5 21a4.5 4.5 0 1 0 0-9a4.5 4.5 0 0 0 0 9m3.5-8L21 3" />
    </svg>
    <span class="block leading h-full leading-8 text-sm">API Key</span>
  </div>
  <Dialog v-model:open="showDialog" closeOnOverlayClick="false">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Set API Key</DialogTitle>
      </DialogHeader>
      <div class="comfy-modal-content-sml">
        <input
          v-model="apiKey"
          type="password"
          placeholder="API Key"
          :class="[{'border-red-500': hasError}, 'border', 'w-full', 'bg-transparent', 'px-2', 'mb-3',]"
          @input="clearError" />
        <p class="py-2">
          Please
          <a class="underline" href="###" @click.prevent="openOAuth">click to login</a>
          and autofill the key,
        </p>
        <p class="py-2">
          or visit
          <a class="underline" href="https://cloud.siliconflow.cn" target="_blank">https://cloud.siliconflow.cn</a>
          to get your key and input manually.
        </p>
        <p class="py-2">
          Setting the API Key signifies agreement to the
          <a class="underline" href="https://docs.siliconflow.cn/docs/user-agreement" target="_blank">User
            Agreement</a>
          and
          <a class="underline" href="https://docs.siliconflow.cn/docs/privacy-policy" target="_blank">Privacy
            Policy.</a>
        </p>
      </div>
      <DialogFooter>
        <Button type="submit" @click="toSubmit">Submit</Button>
        <Button variant="outline" @click="toClose">Close</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import {
  Dialog,
  DialogContent,
  // DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { set_api_key } from '@/api/user'
import { useStatusStore} from '@/stores/userStatus'
import { toast } from 'vue-sonner'

const statusStore = useStatusStore()
const showDialog = ref(false)

const apiKey = ref<string>('');
const hasError = ref<boolean>(false);

const openOAuthPopup = async (setKey: (key: string) => void) => {
  const clientId = 'SFaJLLq0y6CAMoyDm81aMu';
  const ACCOUNT_ENDPOINT = 'https://account.siliconflow.cn';
  const authUrl = `${ACCOUNT_ENDPOINT}/oauth?client_id=${clientId}`;
  const popup = window.open(authUrl, 'oauthPopup', 'width=600,height=600');
  window.addEventListener('message', (event) => {
      if (event.data.length > 0 && event.data[0]['secretKey'] !== undefined) {
          setKey(event.data[0]['secretKey']);
          if (popup) {
            popup.close();
          }
      }
  });
};
function clearError() {
  hasError.value = false;
}
toast('', {
      description: 'API Key set successfully!'
    });
async function toSubmit() {
  if (!apiKey.value) {
    hasError.value = true;
    return false;
  }
  const response = await set_api_key(`api_key=${encodeURIComponent(apiKey.value)}`)
  if (response.ok) {
    toast('', {
      description: 'API Key set successfully!',
      closeButton: true,
    });
    showDialog.value = false;
    statusStore.loginRefresh()
  } else {
    toast('', {
      description: `Failed to set API Key: ${await response.text()}`,
    });
  }
}
function toClose() {
  showDialog.value = false;
  apiKey.value = '';
  hasError.value = false;
}
function openOAuth() {
  openOAuthPopup((key: string) => {
    apiKey.value = key;
  });
}
</script>
<style scoped></style>
