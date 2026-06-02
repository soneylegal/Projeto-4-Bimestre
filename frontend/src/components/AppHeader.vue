<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const route = useRoute()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const pageTitle = computed(() => {
  if (route.name === 'Dashboard') return 'Painel de Controle'
  if (route.name === 'Projects') return 'Meus Projetos'
  if (route.name === 'ProjectDetail') return 'Detalhes do Projeto'
  if (route.name === 'Submissions') return 'Submissões de Tarefas'
  return ''
})

const userInitials = computed(() => {
  if (!user.value?.name) return '?'
  return user.value.name
    .split(' ')
    .map(n => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const handleLogout = async () => {
  await authStore.logout()
}
</script>

<template>
  <header class="app-header glass-card">
    <div class="header-left">
      <h1 class="page-title">{{ pageTitle }}</h1>
    </div>
    
    <div class="header-right" v-if="user">
      <div class="user-profile">
        <div class="user-info">
          <span class="user-name">{{ user.name }}</span>
          <span class="user-email">{{ user.email }}</span>
        </div>
        
        <div class="user-avatar-wrapper">
          <img 
            v-if="user.avatar_url" 
            :src="user.avatar_url" 
            :alt="user.name" 
            class="user-avatar"
          />
          <div v-else class="user-avatar-placeholder">
            {{ userInitials }}
          </div>
        </div>
      </div>
      
      <button class="logout-btn" @click="handleLogout" title="Sair da Conta">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="logout-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  height: var(--header-height);
  width: calc(100% - var(--sidebar-width));
  position: fixed;
  top: 0;
  right: 0;
  z-index: 90;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  border-radius: 0;
  border-top: none;
  border-left: none;
  border-right: none;
  border-bottom: 1px solid var(--border-glass);
  background: var(--bg-glass);
}

.page-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.user-email {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.user-avatar-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 100%;
  height: 100%;
  background: var(--gradient-primary);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
}

.logout-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  border: 1px solid var(--border-glass);
  transition: var(--transition-fast);
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  border-color: rgba(239, 68, 68, 0.2);
}

.logout-icon {
  width: 18px;
  height: 18px;
}
</style>
