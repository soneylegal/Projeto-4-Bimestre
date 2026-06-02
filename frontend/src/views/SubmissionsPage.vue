<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const projectId = computed(() => route.params.id)

const submissions = computed(() => [
  {
    id: 1,
    taskTitle: 'Revisão Bibliográfica',
    filename: 'revisao_literatura_v2.pdf',
    submittedAt: '15/04/2026 às 16:30',
    status: 'approved',
    grade: '10.0',
    comment: 'Excelente revisão bibliográfica. A contextualização sobre os sensores de baixo custo ficou muito completa.'
  },
  {
    id: 2,
    taskTitle: 'Montagem dos Sensores de Condutividade',
    filename: 'esquematico_sensores.zip',
    submittedAt: '28/05/2026 às 11:15',
    status: 'pending',
    grade: null,
    comment: null
  }
])

const tasks = computed(() => [
  { id: 2, title: 'Montagem dos Sensores de Condutividade' },
  { id: 3, title: 'Desenvolvimento do Dashboard IoT' }
])

const selectedTask = ref('')
const fileUploaded = ref(null)

const handleUploadMock = () => {
  if (!selectedTask.value) {
    alert('Por favor, selecione uma tarefa.')
    return
  }
  alert('Simulação: Arquivo submetido com sucesso para a tarefa selecionada!')
  fileUploaded.value = null
  selectedTask.value = ''
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

    <div class="submissions-layout">
      <!-- Left side: Submissions history -->
      <div class="history-section">
        <h3 class="section-title">Histórico de Submissões</h3>
        
        <div class="submissions-list">
          <div v-for="sub in submissions" :key="sub.id" class="submission-card glass-card">
            <div class="sub-header">
              <h4 class="task-title">{{ sub.taskTitle }}</h4>
              <span class="status-tag" :class="sub.status">
                {{ sub.status === 'approved' ? 'Aprovado' : 'Aguardando Avaliação' }}
              </span>
            </div>

            <div class="file-details">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="file-icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="file-info">
                <span class="filename">{{ sub.filename }}</span>
                <span class="submitted-date">Enviado em {{ sub.submittedAt }}</span>
              </div>
            </div>

            <div v-if="sub.grade !== null || sub.comment" class="evaluation-box">
              <div class="evaluation-header">
                <span class="evaluation-label">Avaliação do Orientador</span>
                <span v-if="sub.grade" class="grade-badge">Nota: {{ sub.grade }}</span>
              </div>
              <p class="evaluation-comment">{{ sub.comment }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right side: Submit new task -->
      <div class="submit-section">
        <div class="submit-card glass-card">
          <h3 class="section-title">Nova Submissão</h3>
          
          <form @submit.prevent="handleUploadMock" class="submit-form">
            <div class="form-group">
              <label for="task-select" class="form-label">Selecionar Tarefa</label>
              <select id="task-select" v-model="selectedTask" class="form-select">
                <option value="" disabled selected>Escolha uma tarefa...</option>
                <option v-for="task in tasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Upload de Arquivo</label>
              <div class="upload-zone">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="upload-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span class="upload-text">Arraste ou clique para selecionar arquivo</span>
                <span class="upload-limit">PDF, ZIP ou DOCX (Max 10MB)</span>
                <input type="file" class="file-input" @change="e => fileUploaded.value = e.target.files[0]" />
              </div>
              <div v-if="fileUploaded" class="selected-file-preview">
                Arquivo selecionado.
              </div>
            </div>

            <button type="submit" class="btn btn-primary submit-btn">
              Enviar Trabalho
            </button>
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
}

@media (max-width: 992px) {
  .submissions-layout {
    grid-template-columns: 1fr;
  }
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  flex-wrap: wrap;
  gap: 0.5rem;
}

.task-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.status-tag {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.status-tag.approved {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.status-tag.pending {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.file-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.01);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
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
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.evaluation-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
}

.grade-badge {
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--gradient-primary);
  color: #ffffff;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
}

.evaluation-comment {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.submit-card {
  padding: 1.5rem;
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

.form-select {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  transition: var(--transition-fast);
}

.form-select:focus {
  border-color: var(--color-primary);
}

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
  font-size: 0.875rem;
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
  font-size: 0.75rem;
  color: var(--color-accent);
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
}
</style>
