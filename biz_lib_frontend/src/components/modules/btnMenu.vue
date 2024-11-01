<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <div>
        <div class="flex items-center hover:bg-[#4A238E] cursor-pointer relative px-3">
          <span class="mr-1">
            <slot />
          </span>
          <span class="block leading h-full leading-8 text-sm">{{ buttonText }}</span>
          <img v-if="isJson" class="absolute right-1 bottom-0 w-3 h-3" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARzQklUCAgICHwIZIgAAACbSURBVFiF7ZYhEsIwFERfOpFIBAJZgeQoCG7CcThKy2lqEByhM4tIDSBIQyiIfS4z+X9fVBYqIilK2tTcOSd8J2lQopMUlxY465FjzlxT0aF9Oq+WFijCAhawgAUsYIGfC0RIZQI48fqlzmFfJDA1lw7YfhBeTAOsvxQ+ZgmEEK7ApXL4DehzLgZIbRY4kFmj3jAC/fQwY4z5f+5uET1JRps4hQAAAABJRU5ErkJggg==" alt="">
        </div>
      </div>
    </DropdownMenuTrigger>
    <DropdownMenuContent class="w-auto">
      <DropdownMenuGroup>
        <div v-for="(e, i) in objectToArray(showCases)" :key="i">
          <div v-if="judgeType(e.value)">
            <DropdownMenuItem @click="toDo(e)">
              <span>{{ e.name }}</span>
            </DropdownMenuItem>
          </div>
          <div v-else>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <span>{{ e.name }}</span>
              </DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent>
                  <DropdownMenuItem v-for="(item, index) in objectToArray(e.value)" :key="index" @click="toDo(item)">
                    <span>{{ item.name }}</span>
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>
          </div>
        </div>
      </DropdownMenuGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
<script setup lang="ts">
import { inject, ref, watch } from 'vue';
import { objectToArray } from '@/utils/tool'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
const props = defineProps({
  show_cases: Object,
  buttonText: String,
  icon: String,
  isJson: Boolean
})
const showCases = ref(props.show_cases)
const comfyUIApp: any = inject('comfyUIApp');
const popoverShow = ref(false);

const toDo = async (e: any) => {
  if (typeof e.value === 'function') {
    e.value()
    return
  }
  if (e.value.startsWith("https://")) {
    window.open(e.value, '_blank');
  } else if (e.value.endsWith(".json")) {
    const res = await fetch("api/bizyair/workflow", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ file: e.value }),
    });
    const showcase_graph = await res.json()
    comfyUIApp.graph.clear()
    await comfyUIApp.loadGraphData(showcase_graph)
  }
  popoverShow.value = false;
}
const judgeType = (e: any) => {
  return typeof e === 'string' || typeof e === 'function'
}
watch(() => props.show_cases, (val) => {
  if (val) {
    showCases.value = val
  }
})
</script>
<style scoped></style>
