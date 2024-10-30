<script setup lang="ts">
// import btnApiKey from '@/components/btnApiKey.vue'
import btnApiKey from '@/views/btnApiKey/index.vue'
</script>
<template>
  <h2 class="bizyair-logo"></h2>
  <div class="bizyair-menu"><strong>BizyAir</strong>
    <div class="bizyair-menu-item">
      <div class="menus-item menus-item-example">Examples<span class="menus-item-arrow"></span></div>
      <btnApiKey />
      <div class="menus-item menus-item-model">Model</div>
      <div class="menus-item menus-item-news">News<span class="menus-item-arrow"></span></div>
    </div>
  </div>
</template>

<style scoped></style>
