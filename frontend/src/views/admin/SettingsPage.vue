<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'
import { useNotificationStore } from '@/store/notifications'

const notify = useNotificationStore()
const saving = ref(false)

const settings = ref({
  allow_registration: true,
  max_projects_per_advisor: 10,
  submission_deadline_days: 30
})

onMounted(async () => {
  try {
    const res = await apiFetch('/api/admin/settings', { method: 'GET' })
    if (res.ok) {
      const data = await res.json()
      settings.value = { ...settings.value, ...data }
    }
  } catch (e) {
    console.error('Erro ao carregar configurações:', e)
  }
})

async function save() {
  saving.value = true
  try {
    const res = await apiFetch('/api/admin/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings.value)
    })
    if (res.ok) {
      notify.add('Configurações salvas com sucesso', 'success')
    } else {
      notify.add('Erro ao salvar configurações', 'error')
    }
  } catch (e) {
    notify.add('Erro ao salvar configurações', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="settings-page">
    <div class="form-group">
      <label class="form-label">
        <input v-model="settings.allow_registration" type="checkbox" class="form-checkbox" />
        Permitir registro de novos usuários
      </label>
    </div>

    <div class="form-group">
      <label class="form-label">Máximo de projetos por orientador</label>
      <input v-model.number="settings.max_projects_per_advisor" type="number" class="form-input" min="1" max="50" />
    </div>

    <div class="form-group">
      <label class="form-label">Prazo de submissão (dias)</label>
      <input v-model.number="settings.submission_deadline_days" type="number" class="form-input" min="1" max="365" />
    </div>

    <button class="btn btn-primary" :disabled="saving" @click="save">
      {{ saving ? 'Salvando...' : 'Salvar Configurações' }}
    </button>
  </div>
</template>

<style scoped>
.settings-page {
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  max-width: 200px;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}
</style>
