<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const userRoleLabel = computed(() => {
  if (!user.value) return ''
  switch (user.value.role) {
    case 'admin': return 'Administrador'
    case 'advisor': return 'Professor Orientador'
    case 'student': return 'Estudante'
    default: return 'Usuário'
  }
})

// Dynamic metrics mock depending on user type
const stats = computed(() => {
  if (user.value?.role === 'advisor') {
    return [
      { label: 'Projetos Orientados', value: '4', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', color: 'indigo' },
      { label: 'Bolsistas Ativos', value: '8', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z', color: 'emerald' },
      { label: 'Submissões pendentes', value: '3', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', color: 'amber' }
    ]
  }
  
  return [
    { label: 'Projetos Vinculados', value: '2', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', color: 'indigo' },
    { label: 'Minhas Tarefas', value: '5', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01', color: 'emerald' },
    { label: 'Entregas Concluídas', value: '12', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', color: 'accent' }
  ]
})
</script>

<template>
  <div class="dashboard-container" v-if="user">
    <!-- Welcome banner -->
    <div class="welcome-banner glass-card">
      <div class="welcome-text">
        <h2 class="welcome-title">Olá, {{ user.name }}! 👋</h2>
        <p class="welcome-subtitle">Bem-vindo de volta. Aqui está um resumo das atividades do seu perfil de <strong>{{ userRoleLabel }}</strong>.</p>
      </div>
      <div class="user-meta-details">
        <div class="meta-item">
          <span class="meta-label">Matrícula SUAP</span>
          <span class="meta-value">{{ user.suap_id }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">E-mail Institucional</span>
          <span class="meta-value">{{ user.email }}</span>
        </div>
      </div>
    </div>

    <!-- Stat cards grid -->
    <div class="stats-grid">
      <div 
        v-for="stat in stats" 
        :key="stat.label" 
        class="stat-card glass-card"
        :class="stat.color"
      >
        <div class="stat-icon-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="stat-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.icon" />
          </svg>
        </div>
        <div class="stat-data">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Dashboard Content Sections -->
    <div class="dashboard-content">
      <div class="content-card glass-card">
        <h3 class="section-title">Atividades Recentes</h3>
        <div class="activity-list">
          <div class="activity-item">
            <div class="activity-dot indigo"></div>
            <div class="activity-info">
              <p class="activity-text">Você foi vinculado ao projeto <strong>"Monitoramento Hídrico Sustentável"</strong></p>
              <span class="activity-time">Há 2 horas</span>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-dot success"></div>
            <div class="activity-info">
              <p class="activity-text">Tarefa <strong>"Revisão Bibliográfica"</strong> concluída e submetida</p>
              <span class="activity-time">Ontem</span>
            </div>
          </div>
          <div class="activity-item">
            <div class="activity-dot warning"></div>
            <div class="activity-info">
              <p class="activity-text">Reunião de alinhamento com orientador agendada para <strong>Quinta-feira às 14h</strong></p>
              <span class="activity-time">Há 2 dias</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="content-card glass-card">
        <h3 class="section-title">Próximas Entregas</h3>
        <div class="deadline-list">
          <div class="deadline-item">
            <div class="deadline-date">
              <span class="day">10</span>
              <span class="month">Jun</span>
            </div>
            <div class="deadline-info">
              <p class="deadline-text">Relatório Parcial de Atividades</p>
              <span class="deadline-tag danger">Urgente</span>
            </div>
          </div>
          <div class="deadline-item">
            <div class="deadline-date">
              <span class="day">25</span>
              <span class="month">Jun</span>
            </div>
            <div class="deadline-info">
              <p class="deadline-text">Diagrama de Arquitetura de Software</p>
              <span class="deadline-tag info">No prazo</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.welcome-banner {
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
  background: var(--gradient-glass);
}

.welcome-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.welcome-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.user-meta-details {
  display: flex;
  gap: 2rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  font-weight: 600;
}

.meta-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 0.25rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: var(--transition-normal);
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon {
  width: 28px;
  height: 28px;
}

.stat-data {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: 'Outfit', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* Card color modifiers */
.stat-card.indigo .stat-icon-wrapper {
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(99, 102, 241, 0.2);
}
.stat-card.indigo:hover {
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.15);
}

.stat-card.emerald .stat-icon-wrapper {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-accent);
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.stat-card.emerald:hover {
  border-color: rgba(16, 185, 129, 0.3);
  box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.15);
}

.stat-card.amber .stat-icon-wrapper {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}
.stat-card.amber:hover {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.15);
}

.stat-card.accent .stat-icon-wrapper {
  background: rgba(139, 92, 246, 0.1);
  color: var(--color-secondary);
  border: 1px solid rgba(139, 92, 246, 0.2);
}
.stat-card.accent:hover {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 10px 20px -5px rgba(139, 92, 246, 0.15);
}

.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 992px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

.content-card {
  padding: 1.75rem;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 0.75rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.activity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 0.35rem;
  flex-shrink: 0;
}

.activity-dot.indigo { background-color: var(--color-primary); }
.activity-dot.success { background-color: var(--color-success); }
.activity-dot.warning { background-color: var(--color-warning); }

.activity-info {
  display: flex;
  flex-direction: column;
}

.activity-text {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.activity-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.deadline-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.deadline-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.deadline-date {
  width: 50px;
  height: 50px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  line-height: 1.1;
}

.deadline-date .day {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
}

.deadline-date .month {
  font-size: 0.675rem;
  text-transform: uppercase;
  color: var(--text-muted);
}

.deadline-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.deadline-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.deadline-tag {
  font-size: 0.675rem;
  font-weight: 600;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  width: fit-content;
  text-transform: uppercase;
}

.deadline-tag.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.deadline-tag.info {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}
</style>
