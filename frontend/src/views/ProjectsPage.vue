<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../store/auth'
import { apiFetch } from '@/utils/api'

const authStore = useAuthStore()
const projects = ref([])
const students = ref([])
const loading = ref(true)
const errorMsg = ref('')

// Form state
const showModal = ref(false)
const formTitle = ref('')
const formDescription = ref('')
const formRepoUrl = ref('')
const selectedStudents = ref([])
const submitting = ref(false)
const formError = ref('')

const isAuthorizedToCreate = computed(() => {
  return authStore.user && ['admin', 'coordinator', 'advisor'].includes(authStore.user.role)
})

const fetchProjects = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const response = await apiFetch('/api/projects', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    })
    if (response.ok) {
      projects.value = await response.json()
    } else {
      errorMsg.value = 'Falha ao buscar projetos.'
    }
  } catch (error) {
    console.error(error)
    errorMsg.value = 'Erro de rede ao buscar projetos.'
  } finally {
    loading.value = false
  }
}

const fetchStudents = async () => {
  try {
    const response = await apiFetch('/api/auth/users?role=student', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    })
    if (response.ok) {
      students.value = await response.json()
    }
  } catch (error) {
    console.error('Erro ao buscar estudantes:', error)
  }
}

const openCreateModal = () => {
  formTitle.value = ''
  formDescription.value = ''
  formRepoUrl.value = ''
  selectedStudents.value = []
  formError.value = ''
  showModal.value = true
  fetchStudents()
}

const closeCreateModal = () => {
  showModal.value = false
}

const handleCreateProject = async () => {
  formError.value = ''
  
  if (!formTitle.value.trim()) {
    formError.value = 'O título do projeto é obrigatório.'
    return
  }
  if (!formDescription.value.trim()) {
    formError.value = 'A descrição do projeto é obrigatória.'
    return
  }
  if (selectedStudents.value.length === 0) {
    formError.value = 'É obrigatório selecionar pelo menos 1 estudante.'
    return
  }

  submitting.value = true
  try {
    const response = await apiFetch('/api/projects', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        title: formTitle.value.trim(),
        description: formDescription.value.trim(),
        repository_url: formRepoUrl.value.trim() || null,
        member_ids: selectedStudents.value
      })
    })

    if (response.ok) {
      showModal.value = false
      await fetchProjects()
    } else {
      const data = await response.json()
      formError.value = data.detail || 'Ocorreu um erro ao criar o projeto.'
    }
  } catch (error) {
    console.error(error)
    formError.value = 'Erro de conexão com o servidor.'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<template>
  <div class="projects-container">
    <div class="page-header">
      <div class="header-text">
        <p class="section-description">Gerencie e visualize todos os projetos vinculados à sua conta.</p>
      </div>
      <!-- Novo Projeto (apenas visível para admins/coordenadores/orientadores) -->
      <button 
        v-if="isAuthorizedToCreate" 
        class="btn btn-primary add-btn"
        @click="openCreateModal"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="btn-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Novo Projeto
      </button>
    </div>

    <!-- Feedback States -->
    <div v-if="loading" class="state-card loading-state glass-card">
      <div class="spinner"></div>
      <p>Carregando projetos...</p>
    </div>

    <div v-else-if="errorMsg" class="state-card error-state glass-card">
      <p class="error-text">{{ errorMsg }}</p>
      <button class="btn btn-secondary" @click="fetchProjects">Tentar Novamente</button>
    </div>

    <div v-else-if="projects.length === 0" class="state-card empty-state glass-card">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="empty-icon">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <p>Nenhum projeto encontrado.</p>
    </div>

    <!-- Projects Grid -->
    <div v-else class="projects-grid">
      <div 
        v-for="project in projects" 
        :key="project.id" 
        class="project-card glass-card"
      >
        <div class="card-header">
          <span class="project-members-count">
            {{ project.members.length }} {{ project.members.length === 1 ? 'Membro' : 'Membros' }}
          </span>
          <span class="status-badge active">
            Ativo
          </span>
        </div>
        
        <div class="card-body">
          <h3 class="project-title">{{ project.title }}</h3>
          <p class="project-description">{{ project.description }}</p>
        </div>
        
        <div class="card-footer">
          <div class="project-info">
            <span class="info-label">Coordenador/Orientador</span>
            <span class="info-value">{{ project.advisor ? project.advisor.name : 'Não designado' }}</span>
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

    <!-- Modal Criar Projeto -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal-content glass-card animate-fade-in">
        <div class="modal-header">
          <h2>Novo Projeto Acadêmico</h2>
          <button class="close-btn" @click="closeCreateModal">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="close-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="handleCreateProject" class="modal-form">
          <div class="form-group">
            <label for="title">Título do Projeto <span class="required">*</span></label>
            <input 
              type="text" 
              id="title" 
              v-model="formTitle" 
              placeholder="Ex: Monitoramento Hídrico Sustentável"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label for="description">Descrição / Resumo <span class="required">*</span></label>
            <textarea 
              id="description" 
              v-model="formDescription" 
              placeholder="Descreva os objetivos, metodologia e resultados esperados..."
              class="form-input form-textarea"
              rows="4"
              required
            ></textarea>
          </div>

          <div class="form-group">
            <label for="repoUrl">URL do Repositório (Git) <span class="optional">(Opcional)</span></label>
            <input 
              type="url" 
              id="repoUrl" 
              v-model="formRepoUrl" 
              placeholder="Ex: https://github.com/usuario/projeto"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Selecione os Estudantes Participantes <span class="required">* (Selecione pelo menos 1)</span></label>
            <div class="students-list-container">
              <div v-if="students.length === 0" class="no-students">
                Buscando estudantes ativos...
              </div>
              <div 
                v-else 
                v-for="student in students" 
                :key="student.id" 
                class="student-checkbox-item"
              >
                <input 
                  type="checkbox" 
                  :id="`student-${student.id}`" 
                  :value="student.id" 
                  v-model="selectedStudents"
                  class="checkbox-input"
                />
                <label :for="`student-${student.id}`" class="checkbox-label">
                  <span class="student-name">{{ student.name }}</span>
                  <span class="student-email">{{ student.email }}</span>
                </label>
              </div>
            </div>
          </div>

          <div v-if="formError" class="form-error-banner">
            {{ formError }}
          </div>

          <div class="form-actions">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="closeCreateModal"
              :disabled="submitting"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="submitting"
            >
              {{ submitting ? 'Salvando...' : 'Criar Projeto' }}
            </button>
          </div>
        </form>
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

.page-header {
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
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
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

.project-members-count {
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

/* State Cards */
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

.empty-icon {
  width: 48px;
  height: 48px;
  color: var(--text-muted);
}

.error-text {
  color: var(--color-danger);
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

.students-list-container {
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  background: rgba(15, 23, 42, 0.4);
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.no-students {
  padding: 1rem;
  font-size: 0.875rem;
  color: var(--text-muted);
  text-align: center;
}

.student-checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 4px;
  transition: var(--transition-fast);
  cursor: pointer;
}

.student-checkbox-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

.checkbox-label {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  flex: 1;
}

.student-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.student-email {
  font-size: 0.75rem;
  color: var(--text-muted);
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

.animate-fade-in {
  animation: fadeIn 0.25s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
