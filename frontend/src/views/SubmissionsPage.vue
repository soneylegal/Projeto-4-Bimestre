<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useNotificationStore } from '../store/notifications'

const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const projectId = computed(() => route.params.id)

const project = ref(null)
const submissions = ref([])
const loading = ref(true)
const error = ref(null)

const fileUploaded = ref(null)
const uploadLoading = ref(false)

// Estado para controle de avaliações
const evaluationFeedbacks = ref({})
const evalLoading = ref({})

// Carrega os dados do projeto
const fetchProject = async () => {
  try {
    const response = await fetch(`/api/projects/${projectId.value}`)
    if (response.ok) {
      project.value = await response.json()
    } else {
      throw new Error('Falha ao carregar os dados do projeto.')
    }
  } catch (err) {
    console.error(err)
    error.value = err.message
    notificationStore.add(err.message, 'error')
  }
}

// Carrega o histórico de submissões do projeto
const fetchSubmissions = async () => {
  try {
    const response = await fetch(`/api/submissions/${projectId.value}`)
    if (response.ok) {
      submissions.value = await response.json()
    } else {
      throw new Error('Falha ao carregar o histórico de submissões.')
    }
  } catch (err) {
    console.error(err)
    error.value = err.message
    notificationStore.add(err.message, 'error')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  if (!authStore.user) {
    await authStore.fetchUser()
  }
  await Promise.all([fetchProject(), fetchSubmissions()])
})

// Permissões de Orientador
const isAdvisor = computed(() => {
  if (!project.value || !authStore.user) return false
  return authStore.user.role === 'admin' || 
         authStore.user.role === 'coordinator' || 
         (authStore.user.role === 'advisor' && project.value.advisor_id === authStore.user.id)
})

// Permissões de Membro do Projeto (para Alunos)
const isMember = computed(() => {
  if (!project.value || !authStore.user) return false
  if (authStore.user.role === 'admin' || authStore.user.role === 'coordinator') return true
  return project.value.members.some(m => m.id === authStore.user.id)
})

const isStudent = computed(() => {
  return authStore.user && authStore.user.role === 'student'
})

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    if (file.size > 50 * 1024 * 1024) {
      notificationStore.add('O arquivo não pode exceder o limite de 50 MB.', 'warning')
      fileUploaded.value = null
      e.target.value = ''
      return
    }
    fileUploaded.value = file
  }
}

const handleUpload = async () => {
  if (!fileUploaded.value) {
    notificationStore.add('Selecione um arquivo para enviar.', 'warning')
    return
  }
  uploadLoading.value = true
  error.value = null

  const formData = new FormData()
  formData.append('project_id', projectId.value)
  formData.append('file', fileUploaded.value)

  try {
    const response = await fetch('/api/submissions', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      fileUploaded.value = null
      notificationStore.add('Nova versão submetida com sucesso!', 'success')
      await fetchSubmissions()
    } else {
      const errData = await response.json()
      throw new Error(errData.detail || 'Erro ao enviar o arquivo.')
    }
  } catch (err) {
    error.value = err.message
    notificationStore.add(err.message, 'error')
  } finally {
    uploadLoading.value = false
  }
}

const submitEvaluation = async (submissionId) => {
  const feedbackText = evaluationFeedbacks.value[submissionId]
  if (!feedbackText || !feedbackText.trim()) {
    notificationStore.add('Por favor, insira um comentário ou feedback para a avaliação.', 'warning')
    return
  }

  evalLoading.value[submissionId] = true
  try {
    const response = await fetch(`/api/submissions/${submissionId}/evaluate`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ feedback: feedbackText })
    })

    if (response.ok) {
      evaluationFeedbacks.value[submissionId] = ''
      notificationStore.add('Avaliação e feedback registrados com sucesso!', 'success')
      await fetchSubmissions()
    } else {
      const errData = await response.json()
      throw new Error(errData.detail || 'Erro ao submeter avaliação.')
    }
  } catch (err) {
    notificationStore.add(err.message, 'error')
  } finally {
    evalLoading.value[submissionId] = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="submissions-container">
    <div class="back-navigation">
      <router-link :to="`/projects/${projectId}`" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="back-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Voltar para o Projeto
      </router-link>
    </div>

    <!-- Feedback visual de erros da tela -->
    <div v-if="error" class="alert-error glass-card">
      <div class="alert-content">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="alert-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading-wrapper">
      <div class="spinner"></div>
      <p>Carregando histórico de submissões...</p>
    </div>

    <div v-else class="submissions-layout">
      <!-- Left side: Submissions history -->
      <div class="history-section">
        <h2 class="section-title">Histórico de Entregas</h2>
        
        <div v-if="submissions.length === 0" class="empty-state glass-card">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="empty-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          </svg>
          <p class="empty-text">Nenhum arquivo foi entregue para este projeto ainda.</p>
        </div>

        <div v-else class="submissions-list">
          <div v-for="sub in submissions" :key="sub.id" class="submission-card glass-card">
            <div class="sub-header">
              <div class="version-info">
                <span class="version-badge">Versão {{ sub.version }}</span>
                <span class="status-tag" :class="sub.status">
                  {{ sub.status === 'evaluated' ? 'Avaliado' : 'Aguardando Avaliação' }}
                </span>
              </div>
              
              <!-- Ação de download seguro -->
              <a :href="`/api/submissions/${sub.id}/download`" class="btn btn-secondary btn-sm download-btn">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="btn-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Baixar
              </a>
            </div>

            <div class="file-details">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="file-icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="file-info">
                <span class="filename">{{ sub.filename }}</span>
                <span class="submitted-date">
                  Enviado por <strong>{{ sub.uploader ? sub.uploader.name : 'Membro' }}</strong> em {{ formatDate(sub.created_at) }}
                </span>
              </div>
            </div>

            <!-- Caixa de Feedback da Avaliação -->
            <div v-if="sub.status === 'evaluated'" class="evaluation-box">
              <div class="evaluation-header">
                <span class="evaluation-label">Feedback do Orientador</span>
              </div>
              <p class="evaluation-comment">{{ sub.feedback || 'Entrega avaliada sem comentários adicionais.' }}</p>
            </div>

            <!-- Formulário de Avaliação (exclusivo para orientador responsável) -->
            <div v-else-if="isAdvisor" class="evaluation-form-card">
              <label class="form-label">Avaliação da Entrega</label>
              <textarea 
                v-model="evaluationFeedbacks[sub.id]" 
                placeholder="Insira as observações, correções ou feedback do projeto..." 
                class="feedback-textarea"
              ></textarea>
              <button 
                @click="submitEvaluation(sub.id)" 
                class="btn btn-primary btn-sm eval-submit-btn" 
                :disabled="evalLoading[sub.id]"
              >
                {{ evalLoading[sub.id] ? 'Enviando...' : 'Submeter Avaliação' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right side: Submit new task -->
      <div v-if="isStudent && isMember" class="submit-section">
        <div class="submit-card glass-card">
          <h3 class="section-title">Enviar Trabalho</h3>
          <p class="submit-desc">Envie novas versões de relatórios, códigos ou diagramas do projeto para avaliação.</p>
          
          <form @submit.prevent="handleUpload" class="submit-form">
            <div class="form-group">
              <label class="form-label">Selecionar Arquivo</label>
              <div class="upload-zone">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="upload-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span class="upload-text">Selecione ou arraste o arquivo</span>
                <span class="upload-limit">PDF, ZIP ou DOCX (Max 50MB)</span>
                <input type="file" class="file-input" @change="onFileChange" />
              </div>
              <div v-if="fileUploaded" class="selected-file-preview">
                📎 Selecionado: {{ fileUploaded.name }} ({{ (fileUploaded.size / 1024 / 1024).toFixed(2) }} MB)
              </div>
            </div>

            <button type="submit" class="btn btn-primary submit-btn" :disabled="uploadLoading || !fileUploaded">
              {{ uploadLoading ? 'Enviando...' : 'Enviar Nova Versão' }}
            </button>

            <div v-if="uploadSuccess" class="alert-success-text">
              ✔ Arquivo enviado com sucesso!
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.submissions-container {
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

.submissions-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 992px) {
  .submissions-layout {
    grid-template-columns: 1fr;
  }
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.submission-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.version-badge {
  font-size: 0.85rem;
  font-weight: 700;
  background: var(--gradient-primary);
  color: #ffffff;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-md);
}

.status-tag {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.status-tag.evaluated {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.status-tag.pending {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.download-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  padding: 0.4rem 0.75rem;
}

.btn-icon {
  width: 14px;
  height: 14px;
}

.file-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.02);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-glass);
}

.file-icon {
  width: 24px;
  height: 24px;
  color: var(--color-primary);
}

.file-info {
  display: flex;
  flex-direction: column;
}

.filename {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
}

.submitted-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.evaluation-box {
  background: rgba(99, 102, 241, 0.04);
  border-left: 3px solid var(--color-primary);
  padding: 1rem;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.evaluation-header {
  margin-bottom: 0.5rem;
}

.evaluation-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
}

.evaluation-comment {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Formulário de avaliação */
.evaluation-form-card {
  background: rgba(255, 255, 255, 0.01);
  border-top: 1px solid var(--border-glass);
  padding-top: 1.25rem;
  display: flex;
  flex-direction: column;
}

.feedback-textarea {
  width: 100%;
  min-height: 80px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 0.75rem;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.875rem;
  resize: vertical;
  margin-top: 0.5rem;
  margin-bottom: 0.75rem;
  transition: var(--transition-fast);
}

.feedback-textarea:focus {
  border-color: var(--color-primary);
  outline: none;
}

.eval-submit-btn {
  align-self: flex-start;
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
}

/* Submit section */
.submit-card {
  padding: 1.5rem;
}

.submit-desc {
  font-size: 0.825rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin-bottom: 1.25rem;
}

.submit-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.upload-zone {
  border: 2px dashed var(--border-glass);
  border-radius: var(--radius-md);
  padding: 2.25rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  position: relative;
  transition: var(--transition-fast);
}

.upload-zone:hover {
  border-color: var(--color-primary);
  background: rgba(99, 102, 241, 0.02);
}

.upload-icon {
  width: 32px;
  height: 32px;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.upload-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.upload-limit {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.selected-file-preview {
  font-size: 0.8rem;
  color: var(--color-secondary);
  font-weight: 600;
  margin-top: 0.25rem;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
}

.alert-success-text {
  font-size: 0.8rem;
  color: var(--color-success);
  font-weight: 600;
  text-align: center;
  margin-top: 0.25rem;
}

/* Loading & Empty State */
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  color: var(--text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s infinite linear;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  gap: 1rem;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: var(--text-muted);
}

.empty-text {
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* Alert Error */
.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 1rem;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #f87171;
  font-size: 0.875rem;
}

.alert-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}
</style>
