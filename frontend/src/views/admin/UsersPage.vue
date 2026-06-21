<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'
import { useNotificationStore } from '@/store/notifications'

const notify = useNotificationStore()

const users = ref([])
const loading = ref(true)
const search = ref('')

const filteredUsers = computed(() => {
  if (!search.value) return users.value
  const q = search.value.toLowerCase()
  return users.value.filter(u =>
    u.name?.toLowerCase().includes(q) ||
    u.email?.toLowerCase().includes(q)
  )
})

const roleLabels = {
  admin: 'Administrador',
  coordinator: 'Coordenador',
  advisor: 'Orientador',
  student: 'Estudante'
}

const roleColors = {
  admin: '#ef4444',
  coordinator: '#ffb400',
  advisor: '#10b981',
  student: '#2c67cd'
}

onMounted(async () => {
  try {
    const res = await apiFetch('/api/auth/users', { method: 'GET' })
    if (res.ok) {
      users.value = await res.json()
    }
  } catch (e) {
    console.error('Erro ao carregar usuários:', e)
  } finally {
    loading.value = false
  }
})

async function deleteUser(id) {
  if (!confirm('Tem certeza que deseja remover este usuário?')) return
  try {
    const res = await apiFetch(`/api/auth/users/${id}`, { method: 'DELETE' })
    if (res.ok) {
      users.value = users.value.filter(u => u.id !== id)
      notify.add('Usuário removido com sucesso', 'success')
    } else {
      notify.add('Erro ao remover usuário', 'error')
    }
  } catch (e) {
    notify.add('Erro ao remover usuário', 'error')
  }
}
</script>

<template>
  <div class="users-page">
    <div class="toolbar">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nome ou email..."
        class="search-input"
      />
      <button class="btn btn-primary" disabled>
        + Novo Usuário
      </button>
    </div>

    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="table-wrapper">
      <table class="users-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Papel</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td class="user-name">{{ user.name }}</td>
            <td class="user-email">{{ user.email }}</td>
            <td>
              <span
                class="role-badge"
                :style="{ background: roleColors[user.role] + '18', color: roleColors[user.role], borderColor: roleColors[user.role] + '30' }"
              >
                {{ roleLabels[user.role] || user.role }}
              </span>
            </td>
            <td class="actions">
              <button class="btn btn-sm btn-secondary" disabled>Editar</button>
              <button class="btn btn-sm btn-danger" @click="deleteUser(user.id)">Excluir</button>
            </td>
          </tr>
          <tr v-if="!filteredUsers.length">
            <td colspan="4" class="empty">Nenhum usuário encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.users-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.toolbar {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
}

.table-wrapper {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  text-align: left;
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  border-bottom: 2px solid var(--border-glass);
}

.users-table td {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-glass);
}

.users-table tr:hover {
  background: var(--bg-tertiary);
}

.role-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}
</style>
