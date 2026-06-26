<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../store/auth'
import { useNotificationStore } from '../store/notifications'
import { apiFetch } from '../utils/api'
import { useHead } from '@unhead/vue'
import { useRoute } from 'vue-router'

const route = useRoute()
useHead({
  title: route.meta.title || 'IFAL Projetos',
  meta: [
    { name: 'description', content: route.meta.description || '' },
  ]
})

const authStore = useAuthStore()
const notify = useNotificationStore()

const saving = ref(false)
const form = ref({
  name: '',
  email: '',
  avatar_url: ''
})

onMounted(() => {
  if (authStore.user) {
    form.value.name = authStore.user.name || ''
    form.value.email = authStore.user.email || ''
    form.value.avatar_url = authStore.user.avatar_url || ''
  }
})

async function saveProfile() {
  saving.value = true
  try {
    const res = await apiFetch('/api/auth/me', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.value.name || undefined,
        email: form.value.email || undefined,
        avatar_url: form.value.avatar_url || undefined
      })
    })
    if (res.ok) {
      const updated = await res.json()
      authStore.user = updated
      notify.add('Perfil atualizado com sucesso', 'success')
    } else {
      const err = await res.json()
      notify.add(err.detail || 'Erro ao atualizar perfil', 'error')
    }
  } catch (e) {
    notify.add('Erro ao atualizar perfil', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="profile-page">
    <h1>Meu Perfil</h1>
    <p class="subtitle">Gerencie suas informações pessoais.</p>

    <div class="profile-card glass-card">
      <div class="avatar-section">
        <div class="avatar">
          <img v-if="form.avatar_url" :src="form.avatar_url" alt="Avatar" />
          <span v-else class="avatar-placeholder">
            {{ (authStore.user?.name || '?')[0] }}
          </span>
        </div>
        <div class="avatar-info">
          <p class="user-role">{{ authStore.user?.role }}</p>
          <p class="user-suap">SUAP: {{ authStore.user?.suap_id }}</p>
        </div>
      </div>

      <form @submit.prevent="saveProfile" class="profile-form">
        <div class="form-group">
          <label>Nome completo</label>
          <input v-model="form.name" type="text" required class="form-input" />
        </div>
        <div class="form-group">
          <label>Email institucional</label>
          <input v-model="form.email" type="email" required class="form-input" />
        </div>
        <div class="form-group">
          <label>URL do avatar</label>
          <input v-model="form.avatar_url" type="url" class="form-input" placeholder="https://..." />
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Salvando...' : 'Salvar alterações' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 640px;
  margin: 0 auto;
}

.profile-page h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.profile-card {
  padding: 2rem;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-glass);
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--border-glass);
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
}

.avatar-info .user-role {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text-primary);
  text-transform: capitalize;
}

.avatar-info .user-suap {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}
</style>
