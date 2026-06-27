<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../../utils/api'
import { useNotificationStore } from '../../store/notifications'
import { useHead } from '@unhead/vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../store/auth'

const route = useRoute()
useHead({
  title: route.meta.title || 'IFAL Projetos',
  meta: [
    { name: 'description', content: route.meta.description || '' },
  ]
})

const authStore = useAuthStore()
const notify = useNotificationStore()
const projects = ref([])
const loading = ref(true)
const selectedProjectId = ref('')
const generatingPdf = ref(false)

onMounted(async () => {
  try {
    const res = await apiFetch('/api/projects', { method: 'GET' })
    if (res.ok) {
      projects.value = await res.json()
    }
  } catch (e) {
    console.error('Erro ao carregar projetos:', e)
  } finally {
    loading.value = false
  }
})

async function downloadPdf() {
  if (!selectedProjectId.value) {
    notify.add('Selecione um projeto primeiro.', 'warning')
    return
  }

  generatingPdf.value = true
  try {
    const res = await apiFetch(`/api/reports/${selectedProjectId.value}/pdf`, {
      method: 'GET'
    })
    if (res.ok) {
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const project = projects.value.find(p => p.id === selectedProjectId.value)
      a.download = `relatorio_${project?.title || 'projeto'}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      notify.add('PDF baixado com sucesso!', 'success')
    } else {
      notify.add('Erro ao gerar PDF', 'error')
    }
  } catch (e) {
    notify.add('Erro ao gerar PDF', 'error')
  } finally {
    generatingPdf.value = false
  }
}
</script>

<template>
  <div class="reports-page">
    <h1>Relatórios Institucionais</h1>
    <p class="subtitle">Exporte relatórios acadêmicos em PDF.</p>

    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="report-grid">
      <div class="report-card glass-card">
        <h3>Relatório de Projetos</h3>
        <p>Exporte um relatório completo do projeto com tarefas, submissões e equipe.</p>
        <div class="report-controls">
          <select v-model="selectedProjectId" class="form-input">
            <option value="">Selecione um projeto...</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
          </select>
          <button
            class="btn btn-primary"
            :disabled="!selectedProjectId || generatingPdf"
            @click="downloadPdf"
          >
            {{ generatingPdf ? 'Gerando...' : 'Baixar PDF' }}
          </button>
        </div>
      </div>
      <div class="report-card glass-card">
        <h3>Relatório de Submissões</h3>
        <p>Submissões agrupadas por período e status de avaliação.</p>
        <button class="btn btn-primary" disabled>Em breve</button>
      </div>
      <div class="report-card glass-card">
        <h3>Relatório de Usuários</h3>
        <p>Usuários cadastrados por papel e vínculo institucional.</p>
        <button class="btn btn-primary" disabled>Em breve</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reports-page {
  max-width: 900px;
  margin: 0 auto;
}

.reports-page h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.report-card {
  padding: 1.5rem;
}

.report-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.report-card p {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.report-controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}
</style>
