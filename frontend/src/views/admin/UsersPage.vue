<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '@/utils/api'
import { useNotificationStore } from '@/store/notifications'

const notify = useNotificationStore()

const users = ref([])
const loading = ref(true)
const search = ref('')
const showModal = ref(false)
const editingUser = ref(null)
const saving = ref(false)

const form = ref({
  suap_id: '',
  name: '',
  email: '',
  role: 'student'
})

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

const isEditing = computed(() => !!editingUser.value)

function openNewUser() {
  editingUser.value = null
  form.value = { suap_id: '', name: '', email: '', role: 'student' }
  showModal.value = true
}

function openEdit(user) {
  editingUser.value = user
  form.value = {
    suap_id: user.suap_id,
    name: user.name,
    email: user.email,
    role: user.role
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingUser.value = null
}

async function saveUser() {
  saving.value = true
  try {
    if (isEditing.value) {
      const res = await apiFetch(`/api/auth/users/${editingUser.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form.value)
      })
      if (res.ok) {
        const updated = await res.json()
        const idx = users.value.findIndex(u => u.id === updated.id)
        if (idx !== -1) users.value[idx] = updated
        notify.add('Usuário atualizado com sucesso', 'success')
        closeModal()
      } else {
        const err = await res.json()
        notify.add(err.detail || 'Erro ao atualizar usuário', 'error')
      }
    } else {
      const res = await apiFetch('/api/auth/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form.value)
      })
      if (res.ok) {
        const created = await res.json()
        users.value.push(created)
        notify.add('Usuário criado com sucesso', 'success')
        closeModal()
      } else {
        const err = await res.json()
        notify.add(err.detail || 'Erro ao criar usuário', 'error')
      }
    }
  } catch (e) {
    notify.add('Erro ao salvar usuário', 'error')
  } finally {
    saving.value = false
  }
}

async function toggleActive(user) {
  try {
    const res = await apiFetch(`/api/auth/users/${user.id}/toggle-active`, { method: 'PATCH' })
    if (res.ok) {
      const updated = await res.json()
      const idx = users.value.findIndex(u => u.id === updated.id)
      if (idx !== -1) users.value[idx] = updated
      notify.add(
        updated.is_active ? 'Usuário ativado' : 'Usuário desativado',
        'success'
      )
    } else {
      const err = await res.json()
      notify.add(err.detail || 'Erro ao alterar status', 'error')
    }
  } catch (e) {
    notify.add('Erro ao alterar status do usuário', 'error')
  }
}

async function deleteUser(id) {
  if (!confirm('Tem certeza que deseja remover este usuário?')) return
  try {
    const res = await apiFetch(`/api/auth/users/${id}`, { method: 'DELETE' })
    if (res.ok) {
      users.value = users.value.filter(u => u.id !== id)
      notify.add('Usuário removido com sucesso', 'success')
    } else {
      const err = await res.json()
      notify.add(err.detail || 'Erro ao remover usuário', 'error')
    }
  } catch (e) {
    notify.add('Erro ao remover usuário', 'error')
  }
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
      <button class="btn btn-primary" @click="openNewUser">
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
            <th>Status</th>
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
            <td>
              <button
                class="toggle-btn"
                :class="user.is_active ? 'active' : 'inactive'"
                @click="toggleActive(user)"
                :title="user.is_active ? 'Desativar usuário' : 'Ativar usuário'"
              >
                {{ user.is_active ? 'Ativo' : 'Inativo' }}
              </button>
            </td>
            <td class="actions">
              <button class="btn btn-sm btn-secondary" @click="openEdit(user)">Editar</button>
              <button class="btn btn-sm btn-danger" @click="deleteUser(user.id)">Excluir</button>
            </td>
          </tr>
          <tr v-if="!filteredUsers.length">
            <td colspan="5" class="empty">Nenhum usuário encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content glass-card">
        <h3>{{ isEditing ? 'Editar Usuário' : 'Novo Usuário' }}</h3>
        <form @submit.prevent="saveUser" class="modal-form">
          <div class="form-group">
            <label>Nome</label>
            <input v-model="form.name" type="text" required class="form-input" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" required class="form-input" />
          </div>
          <div class="form-group">
            <label>SUAP ID</label>
            <input v-model="form.suap_id" type="text" required :disabled="isEditing" class="form-input" />
          </div>
          <div class="form-group">
            <label>Papel</label>
            <select v-model="form.role" class="form-input">
              <option value="student">Estudante</option>
              <option value="advisor">Orientador</option>
              <option value="coordinator">Coordenador</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
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
  vertical-align: middle;
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

.toggle-btn {
  padding: 0.25rem 0.75rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  cursor: pointer;
  transition: var(--transition-normal);
}

.toggle-btn.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border-color: rgba(16, 185, 129, 0.3);
}

.toggle-btn.inactive {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  border-color: rgba(239, 68, 68, 0.3);
}

.toggle-btn:hover {
  opacity: 0.8;
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

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 480px;
  padding: 2rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
}

.modal-content h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}
</style>
