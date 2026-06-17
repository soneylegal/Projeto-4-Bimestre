<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const route = useRoute()
const authStore = useAuthStore()

const userRole = computed(() => authStore.user?.role || 'student')

const menuItems = computed(() => {
  const items = [
    {
      name: 'Dashboard',
      path: '/',
      icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z'
    },
    {
      name: 'Projetos',
      path: '/projects',
      icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z'
    }
  ]

  return items
})

const isActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-logo">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="logo-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <span class="brand-text">IFAL <span class="text-gradient">Projetos</span></span>
    </div>
    
    <nav class="sidebar-menu">
      <router-link 
        v-for="item in menuItems" 
        :key="item.name" 
        :to="item.path" 
        class="menu-item"
        :class="{ active: isActive(item.path) }"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="item-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
        </svg>
        <span>{{ item.name }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <div class="user-role-badge" :class="userRole">
        {{ userRole === 'admin' ? 'Administrador' : userRole === 'coordinator' ? 'Coordenador' : userRole === 'advisor' ? 'Orientador' : 'Estudante' }}
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-glass);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
}

.sidebar-brand {
  height: var(--header-height);
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  gap: 0.75rem;
  border-bottom: 1px solid var(--border-glass);
}

.brand-logo {
  width: 36px;
  height: 36px;
  background: var(--gradient-primary);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  width: 20px;
  height: 20px;
  color: #ffffff;
}

.brand-text {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}

.sidebar-menu {
  flex: 1;
  padding: 1.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: var(--transition-fast);
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-primary);
  transform: translateX(4px);
}

.menu-item.active {
  background: var(--gradient-glass);
  color: var(--color-primary);
  border-left-color: var(--color-primary);
  font-weight: 600;
}

.item-icon {
  width: 20px;
  height: 20px;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-glass);
}

.user-role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
  width: 100%;
}

.user-role-badge.student {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.user-role-badge.advisor {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.user-role-badge.coordinator {
  background: rgba(139, 92, 246, 0.1);
  color: var(--color-secondary);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.user-role-badge.admin {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
}
</style>
