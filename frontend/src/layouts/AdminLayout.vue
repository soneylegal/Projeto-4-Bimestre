<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const tabs = [
  { name: 'Usuários', path: '/admin', exact: true },
  { name: 'Auditoria', path: '/admin/logs' },
  { name: 'Configurações', path: '/admin/settings' }
]

const isActive = (tab) => {
  if (tab.exact) return route.path === tab.path
  return route.path.startsWith(tab.path)
}
</script>

<template>
  <div class="admin-layout">
    <div class="admin-header">
      <h1 class="admin-title">Administração</h1>
      <nav class="admin-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          class="tab-btn"
          :class="{ active: isActive(tab) }"
          @click="router.push(tab.path)"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>
    <div class="admin-content">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  margin-bottom: 2rem;
}

.admin-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.admin-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid var(--border-glass);
  padding-bottom: 0.5rem;
}

.tab-btn {
  padding: 0.5rem 1.25rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.tab-btn.active {
  color: var(--color-primary);
  background: var(--bg-secondary);
  font-weight: 600;
  border-bottom: 2px solid var(--color-primary);
  margin-bottom: -2px;
}
</style>
