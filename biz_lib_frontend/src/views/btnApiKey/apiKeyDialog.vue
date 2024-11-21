<template>
  <v-dialog v-model:open="statusStore.showApiKeyDialog" layoutClass="z-9000" class="max-w-[680px] z-9000" @on-close="statusStore.handleApiKeyDialog(false)">
    <template #title>Set API Key</template>
    <div class="comfy-modal-content-sml">
      <Input
        v-model="apiKey"
        type="password"
        placeholder="API Key"
        :class="[{'border-red-500': hasError}]"
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
    <template #foot>
      <Button type="submit" @click="toSubmit">Submit</Button>
      <Button variant="outline" @click="toClose">Close</Button>
    </template>
  </v-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import vDialog from '@/components/modules/vDialog.vue'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { set_api_key } from '@/api/user'
import { useStatusStore} from '@/stores/userStatus'
import { useToaster } from '@/components/modules/toats/index'

const statusStore = useStatusStore()

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

async function toSubmit() {
  if (!apiKey.value) {
    hasError.value = true;
    return false;
  }
  const response = await set_api_key(`api_key=${encodeURIComponent(apiKey.value)}`)
  if (response.ok) {
    useToaster('API Key set successfully!')
    statusStore.handleApiKeyDialog(false)
    statusStore.loginRefresh()
  } else {
    useToaster.error(`Failed to set API Key: ${await response.text()}`)
  }
}
function toClose() {
  statusStore.handleApiKeyDialog(false)
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
