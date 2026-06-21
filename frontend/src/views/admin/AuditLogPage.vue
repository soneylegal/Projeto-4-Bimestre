<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'

const logs = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await apiFetch('/api/admin/logs', { method: 'GET' })
    if (res.ok) {
      logs.value = await res.json()
    }
  } catch (e) {
    console.error('Erro ao carregar logs:', e)
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('pt-BR')
}
</script>

<template>
  <div class="audit-page">
    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="table-wrapper">
      <table class="logs-table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Usuário</th>
            <th>Ação</th>
            <th>Detalhes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td class="log-date">{{ formatDate(log.created_at) }}</td>
            <td>{{ log.user_name || log.user_id }}</td>
            <td>
              <span class="action-tag">{{ log.action }}</span>
            </td>
            <td class="log-details">{{ log.details || '-' }}</td>
          </tr>
          <tr v-if="!logs.length">
            <td colspan="4" class="empty">Nenhum registro de auditoria encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.audit-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
}

.table-wrapper {
  overflow-x: auto;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th {
  text-align: left;
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 2px solid var(--border-glass);
}

.logs-table td {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-glass);
}

.logs-table tr:hover {
  background: var(--bg-tertiary);
}

.action-tag {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--bg-tertiary);
  color: var(--color-primary);
}

.log-date {
  white-space: nowrap;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.log-details {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}
</style>
