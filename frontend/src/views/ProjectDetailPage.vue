<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { apiFetch } from '@/utils/api'
import { useNotificationStore } from '../store/notifications'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const projectId = computed(() => route.params.id)
const project = ref(null)
const tasks = ref([])
const loading = ref(true)
const errorMsg = ref('')

// Task Modals State
const showTaskModal = ref(false)
const isEditingTask = ref(false)
const editingTaskId = ref(null)
const taskFormTitle = ref('')
const taskFormDescription = ref('')
const taskFormStatus = ref('todo')
const taskFormAssignedTo = ref('')
const taskFormDueDate = ref('')
const taskFormError = ref('')
const taskSubmitting = ref(false)

// Check if user is member or advisor of the project
const isParticipant = computed(() => {
  if (!authStore.user || !project.value) return false
  if (authStore.user.role === 'admin' || authStore.user.role === 'coordinator') return true
  if (project.value.advisor_id === authStore.user.id) return true
  return project.value.members.some(m => m.id === authStore.user.id)
})

const fetchProjectDetails = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const response = await apiFetch(`/api/projects/${projectId.value}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    })
    if (response.ok) {
      project.value = await response.json()
      // Load tasks
      await fetchTasks()
    } else if (response.status === 404) {
      errorMsg.value = 'Projeto não encontrado.'
      notificationStore.add('Projeto não encontrado.', 'error')
    } else {
      errorMsg.value = 'Falha ao carregar detalhes do projeto.'
      notificationStore.add('Falha ao carregar detalhes do projeto.', 'error')
    }
  } catch (error) {
    console.error(error)
    errorMsg.value = 'Erro de rede ao buscar projeto.'
    notificationStore.add('Erro de rede ao carregar o projeto.', 'error')
  } finally {
    loading.value = false
  }
}

const fetchTasks = async () => {
  try {
    const response = await apiFetch(`/api/tasks?project_id=${projectId.value}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    })
    if (response.ok) {
      tasks.value = await response.json()
    }
  } catch (error) {
    console.error('Erro ao buscar tarefas:', error)
  }
}

// Kanban lists
const todoTasks = computed(() => tasks.value.filter(t => t.status === 'todo'))
const inProgressTasks = computed(() => tasks.value.filter(t => t.status === 'in_progress'))
const doneTasks = computed(() => tasks.value.filter(t => t.status === 'done'))

const getAssigneeName = (assignedId) => {
  if (!assignedId) return 'Não atribuída'
  if (project.value?.advisor?.id === assignedId) return project.value.advisor.name
  const member = project.value?.members.find(m => m.id === assignedId)
  return member ? member.name : 'Desconhecido'
}

const formatDate = (dateStr) => {
  if (!dateStr) return null
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return null
  return date.toLocaleDateString('pt-BR')
}

// Task Status Transitions
const moveTask = async (task, newStatus) => {
  try {
    const response = await apiFetch(`/api/tasks/${task.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ status: newStatus })
    })
    if (response.ok) {
      notificationStore.add('Status da tarefa atualizado com sucesso!', 'success')
      await fetchTasks()
    } else {
      notificationStore.add('Falha ao mover tarefa.', 'error')
    }
  } catch (error) {
    console.error('Erro ao atualizar status da tarefa:', error)
    notificationStore.add('Erro ao atualizar status da tarefa.', 'error')
  }
}

// Task CRUD Modals
const openCreateTaskModal = () => {
  isEditingTask.value = false
  editingTaskId.value = null
  taskFormTitle.value = ''
  taskFormDescription.value = ''
  taskFormStatus.value = 'todo'
  taskFormAssignedTo.value = ''
  taskFormDueDate.value = ''
  taskFormError.value = ''
  showTaskModal.value = true
}

const openEditTaskModal = (task) => {
  isEditingTask.value = true
  editingTaskId.value = task.id
  taskFormTitle.value = task.title
  taskFormDescription.value = task.description
  taskFormStatus.value = task.status
  taskFormAssignedTo.value = task.assigned_to || ''
  taskFormDueDate.value = task.due_date ? task.due_date.substring(0, 10) : ''
  taskFormError.value = ''
  showTaskModal.value = true
}

const closeTaskModal = () => {
  showTaskModal.value = false
}

const handleSaveTask = async () => {
  taskFormError.value = ''
  if (!taskFormTitle.value.trim()) {
    taskFormError.value = 'O título da tarefa é obrigatório.'
    return
  }
  if (!taskFormDescription.value.trim()) {
    taskFormError.value = 'A descrição da tarefa é obrigatória.'
    return
  }

  taskSubmitting.value = true
  try {
    let response
    const payload = {
      title: taskFormTitle.value.trim(),
      description: taskFormDescription.value.trim(),
      assigned_to: taskFormAssignedTo.value || null,
      due_date: taskFormDueDate.value ? new Date(taskFormDueDate.value + 'T12:00:00').toISOString().substring(0, 19) : null
    }

    if (isEditingTask.value) {
      // For editing task, we must pass status as well
      payload.status = taskFormStatus.value
      response = await apiFetch(`/api/tasks/${editingTaskId.value}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload)
      })
    } else {
      // For creating task, project_id is passed as query param
      response = await apiFetch(`/api/tasks?project_id=${projectId.value}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload)
      })
    }

    if (response.ok) {
      showTaskModal.value = false
      notificationStore.add(isEditingTask.value ? 'Tarefa atualizada com sucesso!' : 'Tarefa criada com sucesso!', 'success')
      await fetchTasks()
    } else {
      const data = await response.json()
      taskFormError.value = data.detail || 'Ocorreu um erro ao salvar a tarefa.'
      notificationStore.add(taskFormError.value, 'error')
    }
  } catch (error) {
    console.error(error)
    taskFormError.value = 'Erro ao conectar ao servidor.'
    notificationStore.add('Erro ao conectar ao servidor.', 'error')
  } finally {
    taskSubmitting.value = false
  }
}

const handleDeleteTask = async (taskId) => {
  if (!confirm('Deseja realmente excluir esta tarefa?')) return
  try {
    const response = await apiFetch(`/api/tasks/${taskId}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      }
    })
    if (response.ok) {
      notificationStore.add('Tarefa excluída com sucesso!', 'success')
      await fetchTasks()
    } else {
      notificationStore.add('Falha ao excluir tarefa.', 'error')
    }
  } catch (error) {
    console.error('Erro ao excluir tarefa:', error)
    notificationStore.add('Erro ao excluir tarefa.', 'error')
  }
}

onMounted(() => {
  fetchProjectDetails()
})
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

    <!-- Feedback States -->
    <div v-if="loading" class="state-card loading-state glass-card">
      <div class="spinner"></div>
      <p>Carregando dados do projeto...</p>
    </div>

    <div v-else-if="errorMsg" class="state-card error-state glass-card">
      <p class="error-text">{{ errorMsg }}</p>
      <button class="btn btn-secondary" @click="fetchProjectDetails">Tentar Novamente</button>
    </div>

    <!-- Main Content -->
    <div v-else-if="project" class="project-content-layout">
      <!-- Project banner header -->
      <div class="project-header glass-card">
        <div class="header-main">
          <div class="header-tag-row">
            <span class="project-tag">Projeto Acadêmico</span>
            <span class="status-badge active">Ativo</span>
          </div>
          <h2 class="project-title">{{ project.title }}</h2>
          <p class="project-desc">{{ project.description }}</p>
          
          <div v-if="project.repository_url" class="project-repo-link">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="repo-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            <a :href="project.repository_url" target="_blank" rel="noopener">{{ project.repository_url }}</a>
          </div>
        </div>
        
        <div class="project-meta">
          <div class="meta-card">
            <span class="meta-label">Coordenador/Orientador</span>
            <span class="meta-value">{{ project.advisor ? project.advisor.name : 'Não designado' }}</span>
          </div>
          <div class="meta-card">
            <span class="meta-label">Integrantes Alunos</span>
            <span class="meta-value">{{ project.members.length }} cadastrados</span>
          </div>
        </div>

        <div class="project-actions-row">
          <router-link :to="`/projects/${projectId}/submissions`" class="btn btn-primary submissions-action-btn">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="btn-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Entregas e Submissões
          </router-link>
        </div>
      </div>

      <!-- Detail section grid -->
      <div class="details-grid">
        <!-- Team Sidebar -->
        <div class="detail-card team-card glass-card">
          <h3 class="section-title">Equipe do Projeto</h3>
          <div class="members-list">
            <!-- Coordinator -->
            <div v-if="project.advisor" class="member-item advisor-item">
              <div class="member-avatar">
                {{ project.advisor.name.charAt(0) }}
              </div>
              <div class="member-info">
                <span class="member-name">{{ project.advisor.name }}</span>
                <span class="member-role">Orientador Coordenador</span>
              </div>
            </div>
            <!-- Students -->
            <div v-for="member in project.members" :key="member.id" class="member-item">
              <div class="member-avatar student">
                {{ member.name.charAt(0) }}
              </div>
              <div class="member-info">
                <span class="member-name">{{ member.name }}</span>
                <span class="member-role">Estudante Membro</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Kanban Board -->
        <div class="detail-card kanban-card glass-card">
          <div class="kanban-header">
            <h3 class="section-title">Quadro Kanban</h3>
            <!-- Add Task button visible only to project participants -->
            <button 
              v-if="isParticipant" 
              class="btn btn-primary add-task-btn"
              @click="openCreateTaskModal"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="btn-icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Nova Tarefa
            </button>
          </div>

          <!-- Kanban Grid -->
          <div class="kanban-board-grid">
            <!-- A Fazer (todo) -->
            <div class="kanban-column">
              <div class="column-header">
                <span class="column-title">A Fazer</span>
                <span class="column-badge">{{ todoTasks.length }}</span>
              </div>
              <div class="column-body">
                <div v-if="todoTasks.length === 0" class="empty-column-text">Sem tarefas</div>
                <div 
                  v-else 
                  v-for="task in todoTasks" 
                  :key="task.id" 
                  class="kanban-task-card glass-card"
                  :class="{ overdue: task.is_overdue }"
                >
                  <div class="task-card-header">
                    <span v-if="task.is_overdue" class="overdue-badge">Atrasada ⚠️</span>
                  </div>
                  <h4 class="task-card-title">{{ task.title }}</h4>
                  <p class="task-card-desc">{{ task.description }}</p>
                  
                  <div class="task-card-meta">
                    <div class="meta-item">
                      <span class="meta-label">Responsável</span>
                      <span class="meta-val">{{ getAssigneeName(task.assigned_to) }}</span>
                    </div>
                    <div v-if="task.due_date" class="meta-item">
                      <span class="meta-label">Prazo</span>
                      <span class="meta-val">{{ formatDate(task.due_date) }}</span>
                    </div>
                  </div>

                  <!-- Actions for members -->
                  <div v-if="isParticipant" class="task-card-actions">
                    <div class="utility-actions">
                      <button class="action-btn edit-task" title="Editar" @click="openEditTaskModal(task)">
                        ✏️
                      </button>
                      <button class="action-btn delete-task" title="Excluir" @click="handleDeleteTask(task.id)">
                        🗑️
                      </button>
                    </div>
                    <div class="movement-actions">
                      <button class="btn btn-secondary move-btn" title="Mover para Em Progresso" @click="moveTask(task, 'in_progress')">
                        Avançar ➔
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Em Progresso (in_progress) -->
            <div class="kanban-column">
              <div class="column-header">
                <span class="column-title">Em Progresso</span>
                <span class="column-badge warning">{{ inProgressTasks.length }}</span>
              </div>
              <div class="column-body">
                <div v-if="inProgressTasks.length === 0" class="empty-column-text">Sem tarefas</div>
                <div 
                  v-else 
                  v-for="task in inProgressTasks" 
                  :key="task.id" 
                  class="kanban-task-card glass-card"
                  :class="{ overdue: task.is_overdue }"
                >
                  <div class="task-card-header">
                    <span v-if="task.is_overdue" class="overdue-badge">Atrasada ⚠️</span>
                  </div>
                  <h4 class="task-card-title">{{ task.title }}</h4>
                  <p class="task-card-desc">{{ task.description }}</p>
                  
                  <div class="task-card-meta">
                    <div class="meta-item">
                      <span class="meta-label">Responsável</span>
                      <span class="meta-val">{{ getAssigneeName(task.assigned_to) }}</span>
                    </div>
                    <div v-if="task.due_date" class="meta-item">
                      <span class="meta-label">Prazo</span>
                      <span class="meta-val">{{ formatDate(task.due_date) }}</span>
                    </div>
                  </div>

                  <!-- Actions for members -->
                  <div v-if="isParticipant" class="task-card-actions">
                    <div class="utility-actions">
                      <button class="action-btn edit-task" title="Editar" @click="openEditTaskModal(task)">
                        ✏️
                      </button>
                      <button class="action-btn delete-task" title="Excluir" @click="handleDeleteTask(task.id)">
                        🗑️
                      </button>
                    </div>
                    <div class="movement-actions">
                      <button class="btn btn-secondary move-btn" title="Voltar para A Fazer" @click="moveTask(task, 'todo')">
                        ⬅
                      </button>
                      <button class="btn btn-secondary move-btn" title="Mover para Concluído" @click="moveTask(task, 'done')">
                        Concluir ➔
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Concluído (done) -->
            <div class="kanban-column">
              <div class="column-header">
                <span class="column-title">Concluído</span>
                <span class="column-badge success">{{ doneTasks.length }}</span>
              </div>
              <div class="column-body">
                <div v-if="doneTasks.length === 0" class="empty-column-text">Sem tarefas</div>
                <div 
                  v-else 
                  v-for="task in doneTasks" 
                  :key="task.id" 
                  class="kanban-task-card glass-card"
                >
                  <h4 class="task-card-title">{{ task.title }}</h4>
                  <p class="task-card-desc">{{ task.description }}</p>
                  
                  <div class="task-card-meta">
                    <div class="meta-item">
                      <span class="meta-label">Responsável</span>
                      <span class="meta-val">{{ getAssigneeName(task.assigned_to) }}</span>
                    </div>
                    <div v-if="task.due_date" class="meta-item">
                      <span class="meta-label">Prazo</span>
                      <span class="meta-val">{{ formatDate(task.due_date) }}</span>
                    </div>
                  </div>

                  <!-- Actions for members -->
                  <div v-if="isParticipant" class="task-card-actions">
                    <div class="utility-actions">
                      <button class="action-btn edit-task" title="Editar" @click="openEditTaskModal(task)">
                        ✏️
                      </button>
                      <button class="action-btn delete-task" title="Excluir" @click="handleDeleteTask(task.id)">
                        🗑️
                      </button>
                    </div>
                    <div class="movement-actions">
                      <button class="btn btn-secondary move-btn" title="Voltar para Em Progresso" @click="moveTask(task, 'in_progress')">
                        ⬅ Reabrir
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Criar/Editar Tarefa -->
    <div v-if="showTaskModal" class="modal-backdrop">
      <div class="modal-content glass-card animate-fade-in">
        <div class="modal-header">
          <h2>{{ isEditingTask ? 'Editar Tarefa' : 'Nova Tarefa' }}</h2>
          <button class="close-btn" @click="closeTaskModal">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="close-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="handleSaveTask" class="modal-form">
          <div class="form-group">
            <label for="taskTitle">Título da Tarefa <span class="required">*</span></label>
            <input 
              type="text" 
              id="taskTitle" 
              v-model="taskFormTitle" 
              placeholder="Ex: Desenhar modelo relacional do BD"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label for="taskDescription">Descrição da Tarefa <span class="required">*</span></label>
            <textarea 
              id="taskDescription" 
              v-model="taskFormDescription" 
              placeholder="Descreva detalhadamente o que deve ser feito nesta entrega..."
              class="form-input form-textarea"
              rows="4"
              required
            ></textarea>
          </div>

          <!-- Status option (only visible when editing) -->
          <div v-if="isEditingTask" class="form-group">
            <label for="taskStatus">Status da Tarefa</label>
            <select id="taskStatus" v-model="taskFormStatus" class="form-input">
              <option value="todo">A Fazer</option>
              <option value="in_progress">Em Progresso</option>
              <option value="done">Concluído</option>
            </select>
          </div>

          <div class="form-group">
            <label for="taskAssignedTo">Atribuir a <span class="optional">(Opcional)</span></label>
            <select id="taskAssignedTo" v-model="taskFormAssignedTo" class="form-input">
              <option value="">Ninguém (Não atribuída)</option>
              <option v-if="project?.advisor" :value="project.advisor.id">{{ project.advisor.name }} (Orientador)</option>
              <option v-for="member in project?.members" :key="member.id" :value="member.id">
                {{ member.name }} (Estudante)
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="taskDueDate">Data Limite de Conclusão <span class="optional">(Opcional)</span></label>
            <input 
              type="date" 
              id="taskDueDate" 
              v-model="taskFormDueDate" 
              class="form-input"
            />
          </div>

          <div v-if="taskFormError" class="form-error-banner">
            {{ taskFormError }}
          </div>

          <div class="form-actions">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="closeTaskModal"
              :disabled="taskSubmitting"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="taskSubmitting"
            >
              {{ taskSubmitting ? 'Salvando...' : 'Salvar Tarefa' }}
            </button>
          </div>
        </form>
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
  gap: 1.5rem;
}

.header-tag-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.project-tag {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-primary);
  background: rgba(99, 102, 241, 0.1);
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
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
  max-width: 900px;
}

.project-repo-link {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.repo-icon {
  width: 16px;
  height: 16px;
  color: var(--color-primary);
}

.project-repo-link a {
  color: var(--color-primary);
  text-decoration: none;
  font-family: monospace;
}

.project-repo-link a:hover {
  text-decoration: underline;
}

.project-meta {
  display: flex;
  gap: 2.5rem;
  flex-wrap: wrap;
  border-top: 1px solid var(--border-glass);
  padding-top: 1.5rem;
  margin-top: 0.5rem;
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

.project-actions-row {
  display: flex;
  gap: 0.75rem;
  border-top: 1px solid var(--border-glass);
  padding-top: 1.25rem;
  margin-top: 0.5rem;
}

.submissions-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
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
}

.members-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.25rem;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.02);
}

.advisor-item {
  border-color: rgba(99, 102, 241, 0.2);
  background: rgba(99, 102, 241, 0.03);
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-primary);
}

.member-avatar.student {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: var(--color-success);
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

.kanban-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 0.75rem;
}

.add-task-btn {
  padding: 0.5rem 1rem;
  font-size: 0.825rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-icon {
  width: 14px;
  height: 14px;
}

.kanban-board-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  align-items: start;
}

@media (max-width: 860px) {
  .kanban-board-grid {
    grid-template-columns: 1fr;
  }
}

.kanban-column {
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 450px;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--border-glass);
  padding-bottom: 0.5rem;
  margin-bottom: 0.25rem;
}

.column-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.column-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

.column-badge.warning {
  background: rgba(245, 158, 11, 0.15);
  color: var(--color-warning);
}

.column-badge.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-success);
}

.column-body {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  flex: 1;
}

.empty-column-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  text-align: center;
  padding: 2rem 0;
  border: 1px dashed rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.kanban-task-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: var(--transition-normal);
  cursor: default;
}

.kanban-task-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.15);
}

.kanban-task-card.overdue {
  border-color: rgba(239, 68, 68, 0.3);
  box-shadow: 0 4px 12px -5px rgba(239, 68, 68, 0.2);
}

.task-card-header {
  display: flex;
  justify-content: flex-end;
}

.overdue-badge {
  font-size: 0.675rem;
  font-weight: 700;
  color: var(--color-danger);
  background: rgba(239, 68, 68, 0.15);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.task-card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}

.task-card-desc {
  font-size: 0.825rem;
  color: var(--text-secondary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-card-meta {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 0.6rem;
}

.task-card-meta .meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
}

.task-card-meta .meta-label {
  color: var(--text-muted);
}

.task-card-meta .meta-val {
  font-weight: 600;
  color: var(--text-primary);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 0.6rem;
  margin-top: 0.25rem;
}

.utility-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  cursor: pointer;
  padding: 0.25rem 0.4rem;
  font-size: 0.8rem;
  transition: var(--transition-fast);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.movement-actions {
  display: flex;
  gap: 0.25rem;
}

.move-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-content {
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 2rem;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: rgba(30, 41, 59, 0.8);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-family: 'Outfit', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: var(--transition-fast);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.close-icon {
  width: 24px;
  height: 24px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.required {
  color: var(--color-danger);
}

.optional {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.form-input {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: var(--transition-fast);
  outline: none;
}

.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25);
}

.form-textarea {
  resize: vertical;
}

.form-error-banner {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--color-danger);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
  border-top: 1px solid var(--border-glass);
  padding-top: 1.25rem;
}

/* Spinner and State Cards */
.state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  gap: 1.5rem;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-text {
  color: var(--color-danger);
}

.animate-fade-in {
  animation: fadeIn 0.25s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
