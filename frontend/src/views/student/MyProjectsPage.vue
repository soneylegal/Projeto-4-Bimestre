<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { apiFetch } from '@/utils/api'

const authStore = useAuthStore()
const projects = ref([])
const tasks = ref([])
const submissions = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [projRes, taskRes, subRes] = await Promise.all([
      apiFetch('/api/projects', { method: 'GET' }),
      apiFetch('/api/tasks', { method: 'GET' }),
      apiFetch('/api/submissions', { method: 'GET' })
    ])
    if (projRes.ok) projects.value = await projRes.json()
    if (taskRes.ok) tasks.value = await taskRes.json()
    if (subRes.ok) submissions.value = await subRes.json()
  } catch (e) {
    console.error('Erro ao carregar dados:', e)
  } finally {
    loading.value = false
  }
})

const userProjects = computed(() => {
  if (!authStore.user) return []
  return projects.value.filter(p =>
    p.members?.some(m => m.id === authStore.user.id) ||
    p.advisor_id === authStore.user.id
  )
})

const pendingTasks = computed(() => {
  if (!authStore.user) return []
  return tasks.value.filter(t =>
    t.assigned_to === authStore.user.id &&
    t.status !== 'done'
  )
})

const totalSubmissions = computed(() => {
  if (!authStore.user) return 0
  return submissions.value.filter(s => s.uploader_id === authStore.user.id).length
})
</script>

<template>
  <div class="my-projects">
    <div class="welcome">
      <h1>Meus Projetos</h1>
      <p class="subtitle">Acompanhe seus projetos, tarefas e entregas acadêmicas.</p>
    </div>

    <div v-if="loading" class="loading">Carregando...</div>

    <template v-else>
      <div class="summary-cards">
        <div class="summary-card">
          <span class="summary-value">{{ userProjects.length }}</span>
          <span class="summary-label">Projetos Vinculados</span>
        </div>
        <div class="summary-card">
          <span class="summary-value">{{ pendingTasks.length }}</span>
          <span class="summary-label">Tarefas Pendentes</span>
        </div>
        <div class="summary-card">
          <span class="summary-value">{{ totalSubmissions }}</span>
          <span class="summary-label">Entregas Realizadas</span>
        </div>
      </div>

      <section class="section">
        <h2 class="section-title">Meus Projetos</h2>
        <div v-if="!userProjects.length" class="empty">
          Nenhum projeto vinculado à sua conta.
        </div>
        <div v-else class="project-list">
          <router-link
            v-for="p in userProjects"
            :key="p.id"
            :to="`/projects/${p.id}`"
            class="project-card glass-card"
          >
            <h3 class="project-name">{{ p.title || p.name }}</h3>
            <p v-if="p.description" class="project-desc">{{ p.description }}</p>
          </router-link>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.my-projects {
  max-width: 900px;
  margin: 0 auto;
}

.welcome {
  margin-bottom: 2rem;
}

.welcome h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
}

.summary-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.project-card {
  padding: 1rem 1.25rem;
  cursor: pointer;
  transition: var(--transition-fast);
  text-decoration: none;
  display: block;
}

.project-card:hover {
  border-color: var(--color-primary);
  transform: translateX(4px);
}

.project-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.project-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0.25rem 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 640px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
