<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from './store/auth'
import ToastNotification from './components/ToastNotification.vue'
import { connectSSE, disconnectSSE } from './utils/sse'

const authStore = useAuthStore()

onMounted(() => {
  if (authStore.isAuthenticated) {
    connectSSE()
  }
})

watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    connectSSE()
  } else {
    disconnectSSE()
  }
})

onUnmounted(() => {
  disconnectSSE()
})
</script>

<template>
  <router-view />
  <ToastNotification />
</template>
