<script setup>
import ToastNotification from './components/ToastNotification.vue'
</script>

<template>
  <router-view />
  <ToastNotification />
</template>

<style>
/* Any application-wide resets or styles not in global.css can go here, but currently global.css handles it. */
</style>
