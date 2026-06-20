<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { apiFetch, apiUrl } from '@/utils/api'
import { useNotificationStore } from '../store/notifications'
import SkeletonCard from '../components/SkeletonCard.vue'
import { useHead } from '@unhead/vue'

const route = useRoute()

useHead({
  title: route.meta.title || 'IFAL Projetos',
  meta: [
    { name: 'description', content: route.meta.description || '' },
    { property: 'og:title', content: route.meta.title || 'IFAL Projetos' },
    { property: 'og:description', content: route.meta.description || '' },
  ]
})

const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const projectId = computed(() => route.params.id)

// ── Estado ───────────────────────────────────────────────────────────────────
const project = ref(null)
const submissions = ref([])
const loading = ref(false)
const uploading = ref(false)
const error = ref(null)

// Upload form
const taskTitle = ref('')
const selectedFile = ref(null)

// Modal de avaliação
const evaluating = ref(false)
const evalSubmissionId = ref(null)
const evalFeedback = ref('')
const evalSubmitting = ref(false)

// computed roles
const isAdvisor = computed(() => {
  if (!project.value || !authStore.user) return false
  return authStore.user.role === 'admin' ||
         authStore.user.role === 'coordinator' ||
         (authStore.user.role === 'advisor' && project.value.advisor_id === authStore.user.id)
})

const isMember = computed(() => {
  if (!project.value || !authStore.user) return false
  if (['admin', 'coordinator'].includes(authStore.user.role)) return true
  return project.value.members.some(m => m.id === authStore.user.id)
})

const isStudent = computed(() => {
  return authStore.user && authStore.user.role === 'student'
})

// ── Carregar Dados ────────────────────────────────────────────────────────────
const fetchProject = async () => {
  try {
    const response = await apiFetch(`/api/projects/${projectId.value}`)
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

async function loadSubmissions() {
  try {
    const res = await apiFetch(`/api/submissions/${projectId.value}`)
    if (res.ok) {
      submissions.value = await res.json()
    } else if (res.status === 404) {
      submissions.value = []
    } else {
      error.value = 'Erro ao carregar histórico de submissões.'
    }
  } catch (e) {
    error.value = 'Erro de conexão ao carregar submissões.'
    notificationStore.add(error.value, 'error')
  }
}

onMounted(async () => {
  loading.value = true
  if (!authStore.user) {
    await authStore.fetchUser()
  }
  await Promise.all([fetchProject(), loadSubmissions()])
  loading.value = false
})

// ── Upload de arquivo ─────────────────────────────────────────────────────────
const MAX_SIZE_MB = 50

function handleFileChange(e) {
  const file = e.target.files[0]
  if (!file) return

  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    notificationStore.add(`O arquivo excede o limite de ${MAX_SIZE_MB} MB.`, 'warning')
    selectedFile.value = null
    e.target.value = ''
    return
  }

  selectedFile.value = file
}

async function handleUpload() {
  if (!selectedFile.value) {
    notificationStore.add('Por favor, selecione um arquivo.', 'warning')
    return
  }

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('project_id', projectId.value)
    formData.append('file', selectedFile.value)
    if (taskTitle.value.trim()) {
      formData.append('task_title', taskTitle.value.trim())
    }

    const res = await apiFetch('/api/submissions', {
      method: 'POST',
      body: formData,
    })

    if (res.ok) {
      notificationStore.add('Nova versão submetida com sucesso!', 'success')
      taskTitle.value = ''
      selectedFile.value = null
      await loadSubmissions()
    } else {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || 'Erro ao enviar arquivo.')
    }
  } catch (e) {
    notificationStore.add(e.message, 'error')
  } finally {
    uploading.value = false
  }
}

// ── Download ──────────────────────────────────────────────────────────────────
function downloadSubmission(sub) {
  window.open(apiUrl(`/api/submissions/${sub.id}/download`), '_blank')
}

// ── Avaliação ─────────────────────────────────────────────────────────────────
function openEvalModal(sub) {
  evalSubmissionId.value = sub.id
  evalFeedback.value = sub.feedback || ''
  evaluating.value = true
}

function closeEvalModal() {
  evaluating.value = false
  evalSubmissionId.value = null
  evalFeedback.value = ''
}

async function submitEvaluation() {
  if (!evalFeedback.value.trim()) {
    notificationStore.add('Por favor, insira um comentário ou feedback para a avaliação.', 'warning')
    return
  }

  evalSubmitting.value = true
  try {
    const res = await apiFetch(`/api/submissions/${evalSubmissionId.value}/evaluate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback: evalFeedback.value.trim() }),
    })

    if (res.ok) {
      notificationStore.add('Avaliação e feedback registrados com sucesso!', 'success')
      closeEvalModal()
      await loadSubmissions()
    } else {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || 'Erro ao avaliar submissão.')
    }
  } catch (e) {
    notificationStore.add(e.message, 'error')
  } finally {
    evalSubmitting.value = false
  }
}

// ── Utilitários ───────────────────────────────────────────────────────────────
function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function statusLabel(s) {
  return s === 'evaluated' ? 'Avaliado' : 'Aguardando Avaliação'
}
</script>

<template>
  <div class="submissions-container">
    <!-- Navegação -->
    <div class="back-navigation">
      <router-link :to="`/projects/${projectId}`" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="back-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Voltar para o Projeto
      </router-link>
    </div>

    <div class="submissions-layout">
      <!-- ── Histórico ──────────────────────────────────────────────── -->
      <div class="history-section">
        <h3 class="section-title">Histórico de Submissões</h3>

        <!-- Loading -->
        <div v-if="loading" class="state-placeholder">
          <SkeletonCard variant="list-item" :count="4" />
        </div>

        <!-- Erro -->
        <div v-else-if="error" class="state-placeholder error-state">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="state-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ error }}</span>
        </div>

        <!-- Vazio -->
        <div v-else-if="submissions.length === 0" class="state-placeholder empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="state-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Nenhuma submissão ainda.<br>Envie o primeiro arquivo pelo formulário ao lado.</span>
        </div>

        <!-- Lista -->
        <div v-else class="submissions-list">
          <div v-for="sub in submissions" :key="sub.id" class="submission-card glass-card">
            <!-- Cabeçalho -->
            <div class="sub-header">
              <div class="sub-title-group">
                <span class="version-badge">v{{ sub.version }}</span>
                <h4 class="task-title">{{ sub.task_title || 'Entrega sem título' }}</h4>
              </div>
              <span class="status-tag" :class="sub.status">
                {{ statusLabel(sub.status) }}
              </span>
            </div>

            <!-- Arquivo -->
            <div class="file-details">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="file-icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="file-info">
                <span class="filename">{{ sub.filename || sub.original_filename }}</span>
                <span class="submitted-date">
                  Enviado por {{ sub.uploader?.name || 'Desconhecido' }} em {{ formatDate(sub.created_at) }}
                </span>
              </div>
              <button @click="downloadSubmission(sub)" class="btn-download" title="Baixar arquivo">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>
            </div>

            <!-- Feedback do orientador -->
            <div v-if="sub.status === 'evaluated'" class="evaluation-box">
              <div class="evaluation-header">
                <span class="evaluation-label">Avaliação do Orientador</span>
              </div>
              <p class="evaluation-comment">{{ sub.feedback }}</p>
            </div>

            <!-- Botão avaliar (orientador) -->
            <div v-if="isAdvisor && sub.status === 'pending'" class="advisor-actions">
              <button @click="openEvalModal(sub)" class="btn btn-outline btn-sm">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Avaliar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Upload ─────────────────────────────────────────────────── -->
      <div v-if="isStudent && isMember" class="submit-section">
        <div class="submit-card glass-card">
          <h3 class="section-title">Nova Submissão</h3>

          <form @submit.prevent="handleUpload" class="submit-form">
            <div class="form-group">
              <label for="task-title-input" class="form-label">Título da Tarefa (opcional)</label>
              <input
                id="task-title-input"
                v-model="taskTitle"
                type="text"
                class="form-input"
                placeholder="Ex: Relatório Parcial — Fase 2"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Arquivo <span class="limit-hint">(máx. 50 MB)</span></label>
              <div class="upload-zone" :class="{ 'has-file': selectedFile }">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="upload-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>

                <template v-if="selectedFile">
                  <span class="upload-text selected">{{ selectedFile.name }}</span>
                  <span class="upload-limit">{{ (selectedFile.size / (1024*1024)).toFixed(2) }} MB selecionado</span>
                </template>
                <template v-else>
                  <span class="upload-text">Arraste ou clique para selecionar</span>
                  <span class="upload-limit">PDF, ZIP, DOCX ou qualquer formato</span>
                </template>

                <input
                  type="file"
                  class="file-input"
                  @change="handleFileChange"
                />
              </div>
            </div>

            <button
              type="submit"
              class="btn btn-primary submit-btn"
              :disabled="uploading || !selectedFile"
            >
              <span v-if="uploading" class="spinner-btn"></span>
              {{ uploading ? 'Enviando...' : 'Enviar Trabalho' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- ── Modal de Avaliação ─────────────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="evaluating" class="modal-overlay" @click.self="closeEvalModal">
        <div class="modal-box glass-card">
          <div class="modal-header">
            <h4 class="modal-title">Avaliar Submissão</h4>
            <button @click="closeEvalModal" class="modal-close">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="form-group">
            <label for="eval-feedback" class="form-label">Feedback para o aluno</label>
            <textarea
              id="eval-feedback"
              v-model="evalFeedback"
              class="form-textarea"
              rows="5"
              placeholder="Descreva os pontos positivos, melhorias necessárias..."
            ></textarea>
          </div>

          <div class="modal-actions">
            <button @click="closeEvalModal" class="btn btn-ghost">Cancelar</button>
            <button
              @click="submitEvaluation"
              class="btn btn-primary"
              :disabled="evalSubmitting || !evalFeedback.trim()"
            >
              <span v-if="evalSubmitting" class="spinner-btn"></span>
              {{ evalSubmitting ? 'Salvando...' : 'Confirmar Avaliação' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.submissions-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Navegação ─────────────────────────────────────────────────────────────── */
.back-navigation { margin-bottom: 0.5rem; }
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
  transition: var(--transition-fast);
}
.back-link:hover { color: var(--color-primary); transform: translateX(-2px); }
.back-icon { width: 16px; height: 16px; }

/* ── Layout ────────────────────────────────────────────────────────────────── */
.submissions-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}
@media (max-width: 992px) {
  .submissions-layout { grid-template-columns: 1fr; }
}

/* ── Títulos ───────────────────────────────────────────────────────────────── */
.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.25rem;
}

/* ── Estados vazio/erro/loading ────────────────────────────────────────────── */
.state-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.875rem;
  line-height: 1.6;
}
.state-icon { width: 40px; height: 40px; opacity: 0.4; }
.error-state { color: var(--color-error, #ef4444); }
.spinner {
  width: 28px; height: 28px;
  border: 3px solid var(--border-glass);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Lista de submissões ───────────────────────────────────────────────────── */
.submissions-list { display: flex; flex-direction: column; gap: 1rem; }

.submission-card {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sub-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sub-title-group { display: flex; align-items: center; gap: 0.625rem; }

.version-badge {
  font-size: 0.7rem;
  font-weight: 800;
  background: var(--gradient-primary);
  color: #fff;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.task-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.status-tag {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: 4px;
  white-space: nowrap;
}
.status-tag.evaluated {
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-success);
}
.status-tag.pending {
  background: rgba(245, 158, 11, 0.12);
  color: var(--color-warning);
}

/* ── Linha do arquivo ─────────────────────────────────────────────────────── */
.file-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255,255,255,0.02);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-glass);
}
.file-icon { width: 22px; height: 22px; color: var(--color-primary); flex-shrink: 0; }
.file-info { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.filename {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.submitted-date { font-size: 0.72rem; color: var(--text-muted); }

.btn-download {
  background: none;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  padding: 0.4rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.btn-download svg { width: 16px; height: 16px; }
.btn-download:hover { color: var(--color-primary); border-color: var(--color-primary); }

/* ── Feedback do orientador ───────────────────────────────────────────────── */
.evaluation-box {
  background: rgba(99, 102, 241, 0.04);
  border-left: 3px solid var(--color-primary);
  padding: 0.875rem 1rem;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.evaluation-header { margin-bottom: 0.4rem; }
.evaluation-label {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}
.evaluation-comment { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5; }

/* ── Ações do orientador ─────────────────────────────────────────────────── */
.advisor-actions { display: flex; justify-content: flex-end; }
.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.4rem 0.875rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-primary);
  background: transparent;
  cursor: pointer;
  transition: var(--transition-fast);
}
.btn-outline svg { width: 14px; height: 14px; }
.btn-outline:hover { background: var(--color-primary); color: #fff; }
.btn-sm { font-size: 0.78rem; padding: 0.35rem 0.75rem; }

/* ── Formulário de Upload ─────────────────────────────────────────────────── */
.submit-card { padding: 1.5rem; }
.submit-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-label { font-size: 0.875rem; font-weight: 600; color: var(--text-secondary); }
.limit-hint { font-size: 0.75rem; font-weight: 400; color: var(--text-muted); }

.form-input {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: var(--transition-fast);
}
.form-input:focus { border-color: var(--color-primary); outline: none; }
.form-input::placeholder { color: var(--text-muted); }

.upload-zone {
  border: 2px dashed var(--border-glass);
  border-radius: var(--radius-md);
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  position: relative;
  transition: var(--transition-fast);
  gap: 0.35rem;
}
.upload-zone:hover, .upload-zone.has-file {
  border-color: var(--color-primary);
  background: rgba(99, 102, 241, 0.03);
}
.upload-icon { width: 30px; height: 30px; color: var(--text-muted); margin-bottom: 0.25rem; }
.upload-text { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); }
.upload-text.selected { color: var(--color-primary); }
.upload-limit { font-size: 0.72rem; color: var(--text-muted); }
.file-input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

.feedback-msg {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
}
.error-msg { background: rgba(239,68,68,0.08); color: #ef4444; }
.success-msg { background: rgba(16,185,129,0.08); color: var(--color-success); }

.submit-btn { width: 100%; padding: 0.75rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner-btn {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ── Modal de Avaliação ───────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.modal-box {
  width: 100%;
  max-width: 480px;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  animation: fadeIn 0.15s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: scale(0.97); } to { opacity: 1; transform: scale(1); } }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}
.modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  transition: var(--transition-fast);
}
.modal-close svg { width: 20px; height: 20px; }
.modal-close:hover { color: var(--text-primary); }

.form-textarea {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  font-size: 0.875rem;
  resize: vertical;
  min-height: 110px;
  transition: var(--transition-fast);
  font-family: inherit;
}
.form-textarea:focus { border-color: var(--color-primary); outline: none; }
.form-textarea::placeholder { color: var(--text-muted); }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
.btn-ghost {
  background: none;
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  padding: 0.6rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}
.btn-ghost:hover { border-color: var(--text-secondary); color: var(--text-primary); }
</style>
