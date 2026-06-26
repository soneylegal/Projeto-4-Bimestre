<script setup>
import { ref, onMounted } from 'vue'
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'
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

const events = ref([])
const loading = ref(true)

const calEvents = ref([])

onMounted(async () => {
  try {
    const res = await apiFetch('/api/calendar/events', { method: 'GET' })
    if (res.ok) {
      events.value = await res.json()
      calEvents.value = events.value.map(e => ({
        id: e.id,
        title: e.title,
        description: e.description,
        start: new Date(e.date),
        end: new Date(e.date),
        class: e.type === 'deadline' ? (e.overdue ? 'event-overdue' : 'event-deadline') : 'event-academic'
      }))
    }
  } catch (err) {
    console.error('Erro ao carregar eventos:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="calendar-page">
    <h1>Calendário Acadêmico</h1>
    <p class="subtitle">Acompanhe prazos de tarefas e eventos acadêmicos.</p>

    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="calendar-wrapper glass-card">
      <VueCal
        :events="calEvents"
        :time="false"
        hide-weekends
        active-view="month"
        locale="pt-br"
        class="custom-calendar"
      />
    </div>
  </div>
</template>

<style scoped>
.calendar-page {
  max-width: 960px;
  margin: 0 auto;
}

.calendar-page h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.loading {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem;
}

.calendar-wrapper {
  padding: 1rem;
  overflow: hidden;
}

:deep(.custom-calendar.vuecal) {
  --vuecal-color-primary: var(--color-primary);
  --vuecal-color-danger: var(--color-danger);
  font-family: inherit;
}

:deep(.custom-calendar .vuecal__menu) {
  background: transparent;
  border-bottom: 1px solid var(--border-glass);
}

:deep(.custom-calendar .vuecal__menu button) {
  color: var(--text-secondary);
}

:deep(.custom-calendar .vuecal__menu button.active) {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

:deep(.custom-calendar .vuecal__title-bar) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

:deep(.custom-calendar .vuecal__cell) {
  background: var(--bg-primary);
  color: var(--text-primary);
  border-color: var(--border-glass);
}

:deep(.custom-calendar .vuecal__cell.today) {
  background: rgba(44, 103, 205, 0.08);
}

:deep(.custom-calendar .vuecal__event) {
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.75rem;
  cursor: pointer;
}

:deep(.event-deadline) {
  background: rgba(16, 185, 129, 0.15);
  color: var(--color-success);
  border-left: 3px solid var(--color-success);
}

:deep(.event-overdue) {
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-danger);
  border-left: 3px solid var(--color-danger);
}

:deep(.event-academic) {
  background: rgba(44, 103, 205, 0.15);
  color: var(--color-primary);
  border-left: 3px solid var(--color-primary);
}
</style>
