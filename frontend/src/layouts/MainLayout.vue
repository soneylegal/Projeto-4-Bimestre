<script setup>
import SidebarNav from '../components/SidebarNav.vue'
import AppHeader from '../components/AppHeader.vue'
</script>

<template>
  <div class="app-layout">
    <SidebarNav />
    
    <div class="content-wrapper">
      <AppHeader />
      
      <main class="main-content">
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
}

.main-content {
  flex: 1;
  padding: calc(var(--header-height) + 2rem) 2rem 2rem 2rem;
  background-color: var(--bg-primary);
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
