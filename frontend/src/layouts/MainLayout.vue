<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import SidebarNav from '../components/SidebarNav.vue'
import AppHeader from '../components/AppHeader.vue'

const sidebarOpen = ref(window.innerWidth >= 768)

const checkScreenSize = () => {
  if (window.innerWidth >= 768) {
    sidebarOpen.value = true
  }
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  if (window.innerWidth < 768) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})
</script>

<template>
  <div class="app-layout">
    <SidebarNav :open="sidebarOpen" @close="closeSidebar" />
    
    <div class="content-wrapper" :class="{ 'sidebar-open': sidebarOpen }">
      <AppHeader @toggle-sidebar="toggleSidebar" />
      
      <main class="main-content" @click="closeSidebar">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.content-wrapper {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content {
  flex: 1;
  padding: calc(var(--header-height) + 2rem) 2rem 2rem 2rem;
  background-color: var(--bg-primary);
}

@media (max-width: 767px) {
  .content-wrapper {
    margin-left: 0;
  }

  .main-content {
    padding: calc(var(--header-height) + 1.5rem) 1rem 1.5rem 1rem;
  }
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
