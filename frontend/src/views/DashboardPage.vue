<script setup>
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '../store/auth'
import { useHead } from '@unhead/vue'
import { useRoute } from 'vue-router'
import SkeletonCard from '../components/SkeletonCard.vue'

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
const user = computed(() => authStore.user)

const roleGradients = {
  admin: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
  coordinator: 'linear-gradient(135deg, #ffb400 0%, #e69500 100%)',
  advisor: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
  student: 'linear-gradient(135deg, #2c67cd 0%, #1d4ed8 100%)'
}

const userRoleLabel = computed(() => {
  if (!user.value) return ''
  switch (user.value.role) {
    case 'admin': return 'Administrador'
    case 'coordinator': return 'Coordenador'
    case 'advisor': return 'Professor Orientador'
    case 'student': return 'Estudante'
    default: return 'Usuário'
  }
})

const roleAccent = computed(() => roleGradients[authStore.role] || roleGradients.student)

const welcomeMessages = computed(() => {
  switch (authStore.role) {
    case 'admin':
      return { title: 'Painel Administrativo', subtitle: 'Você tem controle total sobre o sistema.' }
    case 'coordinator':
      return { title: 'Visão Institucional', subtitle: 'Acompanhe métricas e projetos de toda a instituição.' }
    case 'advisor':
      return { title: 'Painel do Orientador', subtitle: 'Acompanhe seus projetos orientados e avaliações pendentes.' }
    case 'student':
      return { title: 'Meu Painel', subtitle: 'Acompanhe seus projetos, tarefas e entregas.' }
    default:
      return { title: 'Dashboard', subtitle: 'Bem-vindo de volta.' }
  }
})

const loading = ref(true)
const projects = ref([])
const tasks = ref([])
const submissions = ref([])
const totalUsersCount = ref(0)
const totalStudentsCount = ref(0)
const totalAdvisorsCount = ref(0)
const projectsByStatus = ref({})

// Dynamic metrics depending on user role and real data
const stats = computed(() => {
  if (!user.value) return []

  const role = user.value.role

  if (role === 'admin') {
    return [
      { label: 'Total de Projetos', value: projects.value.length.toString(), icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', color: 'indigo' },
      { label: 'Usuários Cadastrados', value: totalUsersCount.value.toString(), icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z', color: 'emerald' },
      { label: 'Submissões no Sistema', value: submissions.value.length.toString(), icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', color: 'accent' }
    ]
  }

  if (role === 'coordinator') {
    const pendingCount = submissions.value.filter(s => s.status === 'pending').length
    return [
      { label: 'Total de Projetos', value: projects.value.length.toString(), icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', color: 'indigo' },
      { label: 'Bolsistas Ativos', value: totalStudentsCount.value.toString(), icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z', color: 'emerald' },
      { label: 'Orientadores Ativos', value: totalAdvisorsCount.value.toString(), icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', color: 'accent' },
      { label: 'Submissões Pendentes', value: pendingCount.toString(), icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', color: 'amber' }
    ]
  }

  if (role === 'advisor') {
    const uniqueMembers = new Set()
    projects.value.forEach(p => {
      if (p.members) {
        p.members.forEach(m => uniqueMembers.add(m.id))
      }
    })
    const pendingCount = submissions.value.filter(s => s.status === 'pending').length
    return [
      { label: 'Projetos Orientados', value: projects.value.length.toString(), icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', color: 'indigo' },
      { label: 'Bolsistas sob Orientação', value: uniqueMembers.size.toString(), icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z', color: 'emerald' },
      { label: 'Entregas Pendentes', value: pendingCount.toString(), icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', color: 'amber' }
    ]
  }

  // Student metrics
  const myTasksCount = tasks.value.filter(t => t.assigned_to === user.value?.id && t.status !== 'done').length
  const completedDeliveries = submissions.value.filter(s => s.uploader_id === user.value?.id).length

  return [
    { label: 'Projetos Vinculados', value: projects.value.length.toString(), icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10', color: 'indigo' },
    { label: 'Minhas Tarefas Pendentes', value: myTasksCount.toString(), icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01', color: 'emerald' },
    { label: 'Minhas Entregas', value: completedDeliveries.toString(), icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', color: 'accent' }
  ]
})

// Deadlines: Tasks not completed
const upcomingDeadlines = computed(() => {
  return tasks.value
    .filter(t => t.status !== 'done' && t.due_date)
    .map(t => {
      const date = new Date(t.due_date)
      const day = date.getDate().toString().padStart(2, '0')
      const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
      const month = monthNames[date.getMonth()]
      
      const diffTime = date.getTime() - new Date().getTime()
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      const isUrgent = diffDays <= 3 || t.is_overdue

      return {
        id: t.id,
        title: t.title,
        day,
        month,
        isUrgent
      }
    })
    .slice(0, 5) // Limit to top 5
})

// Recent activities: derived from tasks and projects
const recentActivities = computed(() => {
  const activities = []
  
  tasks.value.forEach(t => {
    activities.push({
      id: `task-act-${t.id}`,
      text: `Tarefa "${t.title}" atualizada para o status "${t.status === 'done' ? 'Concluído' : t.status === 'in_progress' ? 'Em Progresso' : 'A Fazer'}"`,
      time: t.is_overdue ? 'Atrasada' : 'Recente',
      type: t.status === 'done' ? 'success' : t.status === 'in_progress' ? 'indigo' : 'warning'
    })
  })
  
  projects.value.forEach(p => {
    activities.push({
      id: `proj-act-${p.id}`,
      text: `Vínculo com o projeto "${p.title}" estabelecido`,
      time: 'Registro de Projeto',
      type: 'indigo'
    })
  })

  // Limit to 5 elements
  return activities.slice(0, 5)
})

const fetchDashboardData = async () => {
  try {
    loading.value = true
    const projResp = await fetch('/api/projects')
    if (!projResp.ok) throw new Error('Erro ao buscar projetos.')
    const projList = await projResp.json()
    projects.value = projList

    // Fetch tasks and submissions for all projects in parallel
    const taskPromises = projList.map(p => fetch(`/api/tasks?project_id=${p.id}`).then(r => r.ok ? r.json() : []))
    const subPromises = projList.map(p => fetch(`/api/submissions/${p.id}`).then(r => r.ok ? r.json() : []))
    
    const allTasks = await Promise.all(taskPromises)
    const allSubs = await Promise.all(subPromises)
    
    tasks.value = allTasks.flat()
    submissions.value = allSubs.flat()

    // Additional data fetching for Coordinator and Admin roles
    if (authStore.isAdmin) {
      const usersResp = await fetch('/api/auth/users')
      if (usersResp.ok) {
        const usersList = await usersResp.json()
        totalUsersCount.value = usersList.length
      }
    } else if (authStore.isCoordinator) {
      const [studentsResp, advisorsResp] = await Promise.all([
        fetch('/api/auth/users?role=student'),
        fetch('/api/auth/users?role=advisor')
      ])
      if (studentsResp.ok) {
        const studentsList = await studentsResp.json()
        totalStudentsCount.value = studentsList.length
      }
      if (advisorsResp.ok) {
        const advisorsList = await advisorsResp.json()
        totalAdvisorsCount.value = advisorsList.length
      }
    }

    const statusCount = {}
    projList.forEach(p => {
      const s = p.status || 'active'
      statusCount[s] = (statusCount[s] || 0) + 1
    })
    projectsByStatus.value = statusCount
  } catch (err) {
    console.error('Erro no Dashboard:', err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchUser()
  }
  await fetchDashboardData()
})
</script>

<template>
  <div class="dashboard-container" v-if="user">
    <!-- Welcome banner -->
    <div class="welcome-banner glass-card" :style="{ borderLeftColor: roleAccent, borderLeftWidth: '4px', borderLeftStyle: 'solid' }">
      <div class="welcome-text">
        <h2 class="welcome-title">{{ welcomeMessages.title }}</h2>
        <p class="welcome-subtitle">Olá, <strong>{{ user.name }}</strong>! {{ welcomeMessages.subtitle }}</p>
      </div>
      <div class="user-meta-details">
        <div class="meta-item">
          <span class="meta-label">Papel</span>
          <span class="meta-value">{{ userRoleLabel }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Matrícula SUAP</span>
          <span class="meta-value">{{ user.suap_id }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">E-mail Institucional</span>
          <span class="meta-value">{{ user.email }}</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-wrapper">
      <SkeletonCard variant="stat-card" :count="3" />
      <SkeletonCard variant="text-block" :rows="4" />
    </div>

    <div v-else class="dashboard-data-layout">
      <!-- Stat cards grid -->
      <div class="stats-grid">
        <div 
          v-for="stat in stats" 
          :key="stat.label" 
          class="stat-card glass-card"
          :class="stat.color"
        >
          <div class="stat-icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="stat-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.icon" />
            </svg>
          </div>
          <div class="stat-data">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>

      <!-- Dashboard Content Sections -->
      <div class="dashboard-content">
        <div class="content-card glass-card">
          <h3 class="section-title">Atividades Recentes</h3>
          
          <div v-if="recentActivities.length === 0" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="empty-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="empty-text">Nenhuma atividade recente identificada.</p>
          </div>

          <div v-else class="activity-list">
            <div v-for="act in recentActivities" :key="act.id" class="activity-item">
              <div class="activity-dot" :class="act.type"></div>
              <div class="activity-info">
                <p class="activity-text">{{ act.text }}</p>
                <span class="activity-time">{{ act.time }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="content-card glass-card">
          <h3 class="section-title">Próximas Entregas</h3>

          <div v-if="upcomingDeadlines.length === 0" class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="empty-icon">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="empty-text">Sem prazos de tarefas iminentes.</p>
          </div>

          <div v-else class="deadline-list">
            <div v-for="dl in upcomingDeadlines" :key="dl.id" class="deadline-item">
              <div class="deadline-date">
                <span class="day">{{ dl.day }}</span>
                <span class="month">{{ dl.month }}</span>
              </div>
              <div class="deadline-info">
                <p class="deadline-text">{{ dl.title }}</p>
                <span class="deadline-tag" :class="dl.isUrgent ? 'danger' : 'info'">
                  {{ dl.isUrgent ? 'Urgente' : 'No prazo' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.welcome-banner {
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
  background: var(--gradient-glass);
}

.welcome-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.welcome-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.user-meta-details {
  display: flex;
  gap: 2rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  font-weight: 600;
}

.meta-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: 0.25rem;
}

.dashboard-data-layout {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: var(--transition-normal);
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon {
  width: 28px;
  height: 28px;
}

.stat-data {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: 'Outfit', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* Card color modifiers */
.stat-card.indigo .stat-icon-wrapper {
  background: rgba(25, 136, 44, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(25, 136, 44, 0.2);
}
.stat-card.indigo:hover {
  border-color: rgba(25, 136, 44, 0.3);
  box-shadow: 0 10px 20px -5px rgba(25, 136, 44, 0.15);
}

.stat-card.emerald .stat-icon-wrapper {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.stat-card.emerald:hover {
  border-color: rgba(16, 185, 129, 0.3);
  box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.15);
}

.stat-card.amber .stat-icon-wrapper {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}
.stat-card.amber:hover {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.15);
}

.stat-card.accent .stat-icon-wrapper {
  background: rgba(44, 103, 205, 0.1);
  color: var(--color-secondary);
  border: 1px solid rgba(44, 103, 205, 0.2);
}
.stat-card.accent:hover {
  border-color: rgba(44, 103, 205, 0.3);
  box-shadow: 0 10px 20px -5px rgba(44, 103, 205, 0.15);
}

.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 992px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

.content-card {
  padding: 1.75rem;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-glass);
  padding-bottom: 0.75rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.activity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 0.35rem;
  flex-shrink: 0;
}

.activity-dot.indigo { background-color: var(--color-primary); }
.activity-dot.success { background-color: var(--color-success); }
.activity-dot.warning { background-color: var(--color-warning); }

.activity-info {
  display: flex;
  flex-direction: column;
}

.activity-text {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.activity-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.deadline-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.deadline-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.deadline-date {
  width: 50px;
  height: 50px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  line-height: 1.1;
  flex-shrink: 0;
}

.deadline-date .day {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
}

.deadline-date .month {
  font-size: 0.675rem;
  text-transform: uppercase;
  color: var(--text-muted);
}

.deadline-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.deadline-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.deadline-tag {
  font-size: 0.675rem;
  font-weight: 600;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  width: fit-content;
  text-transform: uppercase;
}

.deadline-tag.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.deadline-tag.info {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

/* Loading & Empty States */
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rem 2rem;
  gap: 1rem;
  color: var(--text-muted);
}

.spinner {
  width: 36px;
  height: 36px;
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
  padding: 3rem 1.5rem;
  text-align: center;
  gap: 0.75rem;
}

.empty-icon {
  width: 40px;
  height: 40px;
  color: var(--text-muted);
}

.empty-text {
  color: var(--text-muted);
  font-size: 0.875rem;
}
</style>
