<script setup>
import { computed } from 'vue'

const projects = computed(() => [
  {
    id: 1,
    title: 'Monitoramento Hídrico Sustentável',
    description: 'Desenvolvimento de uma plataforma IoT de monitoramento e análise em tempo real da qualidade da água em cisternas da região semiárida.',
    coordinator: 'Prof. Augusto César',
    type: 'Pesquisa',
    status: 'active',
    membersCount: 3
  },
  {
    id: 2,
    title: 'Portal de Acessibilidade NEABI',
    description: 'Refatoração e ampliação do portal institucional do Núcleo de Estudos Afro-brasileiros e Indígenas com foco em acessibilidade e design responsivo.',
    coordinator: 'Profª. Maria Silva',
    type: 'Extensão',
    status: 'active',
    membersCount: 4
  },
  {
    id: 3,
    title: 'Biblioteca Digital Raízes Vivas',
    description: 'Desenvolvimento de um acervo digital de literatura afro-brasileira e indígena para catalogação e consulta pública no IFAL.',
    coordinator: 'Prof. Augusto César',
    type: 'Desenvolvimento Tecnológico',
    status: 'completed',
    membersCount: 2
  }
])
</script>

<template>
  <div class="projects-container">
    <div class="page-actions">
      <p class="section-description">Gerencie e visualize todos os projetos vinculados à sua conta.</p>
      <!-- Option to add project (only visible to coordinators/admins, mockup button) -->
      <button class="btn btn-primary add-btn">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="btn-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Novo Projeto
      </button>
    </div>

    <div class="projects-grid">
      <div 
        v-for="project in projects" 
        :key="project.id" 
        class="project-card glass-card"
      >
        <div class="card-header">
          <span class="project-type">{{ project.type }}</span>
          <span class="status-badge" :class="project.status">
            {{ project.status === 'active' ? 'Ativo' : 'Concluído' }}
          </span>
        </div>
        
        <div class="card-body">
          <h3 class="project-title">{{ project.title }}</h3>
          <p class="project-description">{{ project.description }}</p>
        </div>
        
        <div class="card-footer">
          <div class="project-info">
            <span class="info-label">Coordenador</span>
            <span class="info-value">{{ project.coordinator }}</span>
          </div>
          
          <router-link :to="`/projects/${project.id}`" class="btn btn-secondary view-details-btn">
            Visualizar
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="arrow-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.projects-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.page-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-description {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.add-btn {
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1.5rem;
}

.project-card {
  display: flex;
  flex-direction: column;
  padding: 1.75rem;
  transition: var(--transition-normal);
}

.project-card:hover {
  transform: translateY(-4px);
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 12px 24px -10px rgba(99, 102, 241, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.project-type {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-primary);
  background: rgba(99, 102, 241, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.status-badge.completed {
  background: rgba(156, 163, 175, 0.1);
  color: var(--text-secondary);
}

.card-body {
  flex: 1;
  margin-bottom: 1.5rem;
}

.project-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  line-height: 1.3;
}

.project-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-glass);
  padding-top: 1.25rem;
}

.project-info {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.info-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.view-details-btn {
  padding: 0.4rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  gap: 0.25rem;
}

.view-details-btn:hover .arrow-icon {
  transform: translateX(2px);
}

.arrow-icon {
  width: 14px;
  height: 14px;
  transition: var(--transition-fast);
}
</style>
