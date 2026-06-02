<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const projectId = computed(() => route.params.id)

const project = computed(() => ({
  id: projectId.value,
  title: 'Monitoramento Hídrico Sustentável',
  description: 'Desenvolvimento de uma plataforma IoT de monitoramento e análise em tempo real da qualidade da água em cisternas da região semiárida para prever escassez e verificar potabilidade de forma econômica.',
  coordinator: 'Prof. Augusto César',
  type: 'Pesquisa',
  status: 'active',
  startDate: '01/03/2026',
  endDate: '30/11/2026',
  members: [
    { name: 'Ana Souza', role: 'Estudante Bolsista', email: 'ana.souza@ifal.edu.br' },
    { name: 'Lucas Lima', role: 'Estudante Voluntário', email: 'lucas.lima@ifal.edu.br' },
    { name: 'Prof. Augusto César', role: 'Orientador Coordenador', email: 'augusto.cesar@ifal.edu.br' }
  ],
  tasks: [
    { id: 1, title: 'Revisão Bibliográfica', status: 'completed', assignee: 'Ana Souza' },
    { id: 2, title: 'Montagem dos Sensores de Condutividade', status: 'in-progress', assignee: 'Lucas Lima' },
    { id: 3, title: 'Desenvolvimento do Dashboard IoT', status: 'todo', assignee: 'Ana Souza' }
  ]
}))
</script>

<template>
  <div class="project-detail-container">
    <div class="back-navigation">
      <router-link to="/projects" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="back-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Voltar para Projetos
      </router-link>
    </div>

    <!-- Main project banner -->
    <div class="project-header glass-card">
      <div class="header-main">
        <span class="project-type">{{ project.type }}</span>
        <h2 class="project-title">{{ project.title }}</h2>
        <p class="project-desc">{{ project.description }}</p>
      </div>
      <div class="project-meta">
        <div class="meta-card">
          <span class="meta-label">Início</span>
          <span class="meta-value">{{ project.startDate }}</span>
        </div>
        <div class="meta-card">
          <span class="meta-label">Término previsto</span>
          <span class="meta-value">{{ project.endDate }}</span>
        </div>
        <div class="meta-card">
          <span class="meta-label">Coordenador</span>
          <span class="meta-value">{{ project.coordinator }}</span>
        </div>
      </div>
    </div>

    <!-- Details grid -->
    <div class="details-grid">
      <!-- Member section -->
      <div class="detail-card glass-card">
        <h3 class="section-title">Equipe do Projeto</h3>
        <div class="members-list">
          <div v-for="member in project.members" :key="member.name" class="member-item">
            <div class="member-avatar">
              {{ member.name.charAt(0) }}
            </div>
            <div class="member-info">
              <span class="member-name">{{ member.name }}</span>
              <span class="member-role">{{ member.role }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Task section preview (Base to Fase 2 Kanban) -->
      <div class="detail-card glass-card">
        <div class="section-header-action">
          <h3 class="section-title">Tarefas</h3>
          <router-link :to="`/projects/${project.id}/submissions`" class="btn btn-secondary action-btn">
            Submissões
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="btn-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
        
        <div class="tasks-list">
          <div v-for="task in project.tasks" :key="task.id" class="task-item">
            <div class="task-left">
              <span class="task-status-indicator" :class="task.status"></span>
              <span class="task-title">{{ task.title }}</span>
            </div>
            <span class="task-assignee">{{ task.assignee }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-detail-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.back-navigation {
  margin-bottom: 0.5rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
  transition: var(--transition-fast);
}

.back-link:hover {
  color: var(--color-primary);
  transform: translateX(-2px);
}

.back-icon {
  width: 16px;
  height: 16px;
}

.project-header {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.project-type {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-primary);
  background: rgba(99, 102, 241, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  width: fit-content;
  display: inline-block;
  margin-bottom: 0.75rem;
}

.project-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.project-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
  max-width: 800px;
}

.project-meta {
  display: flex;
  gap: 2.5rem;
  flex-wrap: wrap;
  border-top: 1px solid var(--border-glass);
  padding-top: 1.5rem;
}

.meta-card {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.meta-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 0.25rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
}

@media (max-width: 992px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
}

.detail-card {
  padding: 1.75rem;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.25rem;
}

.section-header-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.section-header-action .section-title {
  margin-bottom: 0;
}

.action-btn {
  padding: 0.4rem 1rem;
  font-size: 0.825rem;
  font-weight: 500;
}

.btn-icon {
  width: 14px;
  height: 14px;
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-glass);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-primary);
}

.member-info {
  display: flex;
  flex-direction: column;
}

.member-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.member-role {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
}

.task-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.task-status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.task-status-indicator.completed { background-color: var(--color-success); }
.task-status-indicator.in-progress { background-color: var(--color-warning); }
.task-status-indicator.todo { background-color: var(--text-muted); }

.task-title {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.task-assignee {
  font-size: 0.75rem;
  color: var(--text-muted);
}
</style>
