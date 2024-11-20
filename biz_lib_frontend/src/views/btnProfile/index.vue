<template>
  <div @click="toshowDrawer" variant="outline" class="flex items-center hover:bg-[#4A238E] cursor-pointer relative px-3">
    <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24">
      <g fill="none" stroke="#ddd" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5">
        <circle cx="12" cy="8" r="5" />
        <path d="M20 21a8 8 0 1 0-16 0m16 0a8 8 0 1 0-16 0" />
      </g>
    </svg>
    <span class="block leading h-full leading-8 text-sm">Profile</span>
  </div>
  <vDrawer v-model:open="showDrawer">
    <div class="bizyair-profile-primary flex items-center">
      <img :src="profileImageSrc" alt="Profile Image" />
      <div v-if="statusStore.infoData.name" class="ml-4">{{ statusStore.infoData.name }}</div>
    </div>
    <div class="py-2 flex items-center mt-4">
      <span>API Key:</span>
      <span class="ml-2" id="bizyair-profile-password">
        {{ statusStore.infoData.api_key }}
      </span>
      <vTooltips tips="Edit">
        <FilePenLine @click="statusStore.handleApiKeyDialog(true)" class="ml-2 cursor-pointer" />
      </vTooltips>
      <!-- <vTooltips tips="Copy">
        <Copy @click="statusStore.copyText(statusStore.infoData.api_key)" class="ml-2 cursor-pointer" />
      </vTooltips> -->
    </div>
    <div class="py-2 flex">
      <span>Level:</span>
      <span class="ml-2">{{ levelText }}</span>
    </div>
    <div class="py-2 flex w-full">
      <div class="flex items-center">
        <span class="whitespace-nowrap">Share ID:</span>
        <span class="px-2 ml-2" v-if="!isEditingShareId">
          {{ statusStore.infoData.share_id }}
        </span>
        <Input v-else
          class="px-2 ml-2 border rounded-md box-border h-7"
          ref="shareIdInput"
          v-model="statusStore.infoData.share_id"
          @keyup.enter="saveShareId" />
      </div>
      <div class="flex items-center ml-2">
        <span v-show="!isEditingShareId">
          <vTooltips tips="Edit" v-if="canEditShareId">
            <FilePenLine @click="editShareId" class="ml-2 cursor-pointer" />
          </vTooltips>
          <vTooltips v-else :tips="generateShareIDMessage(statusStore.infoData.last_share_id_update_at)">
            <FilePenLine class="ml-2 cursor-not-allowed" />
          </vTooltips>
        </span>
        <span v-show="isEditingShareId">
          <vTooltips :tips="'Save'">
            <Save @click="saveShareId" class="cursor-pointer" />
          </vTooltips>
        </span>
        <vTooltips :tips="'Copy'">
          <Copy @click="statusStore.copyText(statusStore.infoData.share_id)" class="cursor-pointer ml-2" />
        </vTooltips>
      </div>
    </div>
  </vDrawer>
</template>
<script setup lang="ts">
import { putShareId } from '@/api/user';
import vDrawer from '@/components/modules/vDrawer.vue'
import { FilePenLine, Copy, Save } from 'lucide-vue-next';
import { Input } from '@/components/ui/input'
import vTooltips from '@/components/modules/v-tooltip.vue'
import { useAlertDialog } from '@/components/modules/vAlertDialog'
import { ref, computed } from 'vue'

import { useStatusStore } from '@/stores/userStatus'

const statusStore = useStatusStore()

const profileImageSrc = 'data:image/png;base64,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'
const isEditingShareId = ref(false);
const recordShareId = ref('');
const shareIdInput = ref<HTMLInputElement | null>(null);
const levelMap: { [key: number]: string } = {
  1: 'Trial',
  2: 'Pro',
  3: 'Enterprise',
};
const showDrawer = ref(false)
const levelText = computed(() => levelMap[statusStore.infoData.level]);
const canEditShareId = computed(() => {
  const lastUpdate = new Date(statusStore.infoData.last_share_id_update_at).getTime();
  return !isNaN(lastUpdate) && (Date.now() - lastUpdate > 1000 * 60 * 60 * 24 * 365);
});


const editShareId = () => {
  isEditingShareId.value = true;
  recordShareId.value = statusStore.infoData.share_id;
  setTimeout(() => {
    shareIdInput.value?.focus();
  }, 0);
};

const saveShareId = async () => {
  isEditingShareId.value = false;
  const res = await useAlertDialog({
      title: 'Are you sure you want to modify it?',
      desc: 'If you make this change, it will render any models you have previously shared unavailable, and you are only allowed to make this modification once per year.',
      cancel: 'No, Keep It',
      continue: 'Yes, Delete It',
      z: 'z-9000'
    })
    if (!res) {
      statusStore.infoData.share_id = recordShareId.value;
    } else {
      await putShareId({ share_id: statusStore.infoData.share_id });
      statusStore.loginRefresh()
    }
};

const generateShareIDMessage = (date: string) => {
  const today = new Date(date);
  const nextYear = new Date(today);
  nextYear.setFullYear(today.getFullYear() + 1);
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  };
  return `You can only change your share ID once a year. You need to wait until ${nextYear.toLocaleDateString(
    'en-US',
    options
  )} to make the modification.`;
};
const toshowDrawer = async () => {
  statusStore.loginRefresh()
  showDrawer.value = true
}
</script>
<style scoped></style>
