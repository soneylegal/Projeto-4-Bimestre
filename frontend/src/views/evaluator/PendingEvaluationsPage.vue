<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { apiFetch } from '@/utils/api'

const authStore = useAuthStore()
const submissions = ref([])
const projects = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [subRes, projRes] = await Promise.all([
      apiFetch('/api/submissions', { method: 'GET' }),
      apiFetch('/api/projects', { method: 'GET' })
    ])
    if (subRes.ok) submissions.value = await subRes.json()
    if (projRes.ok) projects.value = await projRes.json()
  } catch (e) {
    console.error('Erro ao carregar dados:', e)
  } finally {
    loading.value = false
  }
})

const pendingSubmissions = computed(() => {
  if (!authStore.user) return []

  const myProjects = new Set()
  if (authStore.isAdvisor) {
    projects.value.forEach(p => {
      if (p.advisor_id === authStore.user.id) myProjects.add(p.id)
    })
  }
  if (authStore.isCoordinator || authStore.isAdmin) {
    projects.value.forEach(p => myProjects.add(p.id))
  }

  return submissions.value.filter(s =>
    s.status === 'pending' &&
    myProjects.has(s.project_id)
  )
})

const getProjectTitle = (projectId) => {
  const p = projects.value.find(p => p.id === projectId)
  return p?.title || p?.name || `Projeto #${projectId}`
}

const statusColors = {
  pending: { bg: '#ffb40018', color: '#ffb400', border: '#ffb40030' },
  approved: { bg: '#10b98118', color: '#10b981', border: '#10b98130' },
  rejected: { bg: '#ef444418', color: '#ef4444', border: '#ef444430' }
}
</script>

<template>
  <div class="pending-page">
    <div class="header">
      <h1>Avaliações Pendentes</h1>
      <p class="subtitle">{{ pendingSubmissions.length }} submissão(ões) aguardando avaliação.</p>
    </div>

    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else-if="!pendingSubmissions.length" class="empty">
      Nenhuma avaliação pendente no momento.
    </div>

    <div v-else class="submission-list">
      <div
        v-for="sub in pendingSubmissions"
        :key="sub.id"
        class="submission-card glass-card"
      >
        <div class="sub-info">
          <router-link
            :to="`/projects/${sub.project_id}/submissions`"
            class="sub-project"
          >
            {{ getProjectTitle(sub.project_id) }}
          </router-link>
          <span class="sub-date">
            {{ new Date(sub.created_at).toLocaleDateString('pt-BR') }}
          </span>
          <span class="sub-file">{{ sub.filename }}</span>
        </div>
        <div class="sub-status">
          <span
            class="status-badge"
            :style="{ background: statusColors.pending.bg, color: statusColors.pending.color, borderColor: statusColors.pending.border }"
          >
            Pendente
          </span>
        </div>
        <router-link
          :to="`/projects/${sub.project_id}/submissions`"
          class="btn btn-sm btn-primary"
        >
          Avaliar
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pending-page {
  max-width: 900px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
}

.submission-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.submission-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
}

.sub-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sub-project {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
}

.sub-project:hover {
  text-decoration: underline;
}

.sub-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.sub-file {
  font-size: 0.825rem;
  color: var(--text-secondary);
}

.sub-status {
  flex-shrink: 0;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
}
</style>
