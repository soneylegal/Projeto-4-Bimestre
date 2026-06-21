<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

defineEmits(['toggle-sidebar'])

const route = useRoute()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const breadcrumbs = computed(() => {
  const list = [{ name: 'Painel', path: '/' }]
  if (route.name === 'Projects') {
    list.push({ name: 'Projetos', path: '/projects' })
  } else if (route.name === 'ProjectDetail') {
    list.push({ name: 'Projetos', path: '/projects' })
    list.push({ name: 'Detalhes', path: route.path })
  } else if (route.name === 'Submissions') {
    list.push({ name: 'Projetos', path: '/projects' })
    const projId = route.params.id
    list.push({ name: 'Detalhes', path: `/projects/${projId}` })
    list.push({ name: 'Submissões', path: route.path })
  }
  return list
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
      <button class="hamburger-btn" @click="$emit('toggle-sidebar')" aria-label="Abrir menu">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="hamburger-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <nav class="breadcrumbs">
        <span v-for="(crumb, idx) in breadcrumbs" :key="crumb.path" class="crumb-wrapper">
          <router-link :to="crumb.path" class="crumb-link">{{ crumb.name }}</router-link>
          <svg v-if="idx < breadcrumbs.length - 1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="crumb-arrow">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </nav>
    </div>

    <div class="header-search">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="search-icon">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input type="text" placeholder="Buscar..." class="search-input" />
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
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.hamburger-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
  background: transparent;
  flex-shrink: 0;
}

.hamburger-btn:hover {
  color: var(--text-primary);
  border-color: var(--color-primary);
}

.hamburger-icon {
  width: 20px;
  height: 20px;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow: hidden;
}

.crumb-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.crumb-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition-fast);
}

.crumb-link:hover {
  color: var(--color-primary);
}

.crumb-arrow {
  width: 12px;
  height: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.header-search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 0.4rem 0.75rem;
  max-width: 260px;
  width: 100%;
  transition: var(--transition-fast);
}

.header-search:focus-within {
  border-color: var(--color-primary);
  background: var(--bg-tertiary);
}

.search-icon {
  width: 16px;
  height: 16px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.825rem;
  width: 100%;
}

.search-input:focus {
  outline: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-shrink: 0;
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
  flex-shrink: 0;
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
  background: transparent;
  cursor: pointer;
  transition: var(--transition-fast);
  flex-shrink: 0;
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

@media (max-width: 767px) {
  .app-header {
    width: 100%;
    padding: 0 1rem;
  }

  .hamburger-btn {
    display: flex;
  }

  .header-search {
    max-width: 140px;
  }
}

@media (max-width: 640px) {
  .header-search {
    display: none;
  }

  .user-email {
    display: none;
  }
}
</style>
