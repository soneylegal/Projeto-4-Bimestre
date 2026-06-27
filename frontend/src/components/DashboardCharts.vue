<script setup>
import { computed } from 'vue'
import { Doughnut, Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Filler
} from 'chart.js'

ChartJS.register(
  ArcElement, Tooltip, Legend,
  CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, Title, Filler
)

const props = defineProps({
  projects: { type: Array, default: () => [] },
  tasks: { type: Array, default: () => [] },
  submissions: { type: Array, default: () => [] }
})

const isDark = computed(() => {
  return document.documentElement.getAttribute('data-theme') !== 'light'
})

const textColor = computed(() => isDark.value ? '#e5e7eb' : '#374151')
const gridColor = computed(() => isDark.value ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)')

const chartColors = {
  todo: '#f59e0b',
  in_progress: '#2c67cd',
  done: '#10b981',
  pending: '#f59e0b',
  evaluated: '#10b981'
}

// ── Projects by Status (Doughnut) ──
const projectStatusData = computed(() => {
  const counts = { active: 0 }
  props.projects.forEach(p => {
    counts.active = (counts.active || 0) + 1
  })
  return {
    labels: Object.keys(counts),
    datasets: [{
      data: Object.values(counts),
      backgroundColor: ['rgba(44, 103, 205, 0.7)'],
      borderColor: ['rgba(44, 103, 205, 1)'],
      borderWidth: 1
    }]
  }
})

// ── Tasks by Status (Doughnut) ──
const taskStatusData = computed(() => {
  const counts = { todo: 0, in_progress: 0, done: 0 }
  props.tasks.forEach(t => {
    if (counts[t.status] !== undefined) counts[t.status]++
  })
  return {
    labels: ['A Fazer', 'Em Progresso', 'Concluído'],
    datasets: [{
      data: [counts.todo, counts.in_progress, counts.done],
      backgroundColor: [
        `${chartColors.todo}cc`,
        `${chartColors.in_progress}cc`,
        `${chartColors.done}cc`
      ],
      borderColor: [chartColors.todo, chartColors.in_progress, chartColors.done],
      borderWidth: 2
    }]
  }
})

// ── Submissions Over Time (Line) ──
const submissionsOverTime = computed(() => {
  const byMonth = {}
  props.submissions.forEach(s => {
    const d = new Date(s.created_at)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    byMonth[key] = (byMonth[key] || 0) + 1
  })
  const sorted = Object.entries(byMonth).sort(([a], [b]) => a.localeCompare(b))
  return {
    labels: sorted.map(([k]) => k),
    datasets: [{
      label: 'Submissões',
      data: sorted.map(([, v]) => v),
      fill: true,
      borderColor: '#2c67cd',
      backgroundColor: 'rgba(44, 103, 205, 0.15)',
      tension: 0.3,
      pointBackgroundColor: '#2c67cd'
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: textColor.value, font: { size: 12 } }
    }
  }
}

const doughnutOptions = {
  ...chartOptions,
  cutout: '60%'
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      ticks: { color: textColor.value },
      grid: { color: gridColor.value }
    },
    y: {
      beginAtZero: true,
      ticks: { color: textColor.value, stepSize: 1 },
      grid: { color: gridColor.value }
    }
  },
  plugins: {
    legend: {
      labels: { color: textColor.value, font: { size: 12 } }
    }
  }
}
</script>

<template>
  <div class="charts-grid">
    <div class="chart-card glass-card">
      <h3 class="chart-title">Tarefas por Status</h3>
      <div class="chart-wrapper">
        <Doughnut :data="taskStatusData" :options="doughnutOptions" />
      </div>
    </div>

    <div class="chart-card glass-card">
      <h3 class="chart-title">Submissões ao Longo do Tempo</h3>
      <div class="chart-wrapper">
        <Line :data="submissionsOverTime" :options="lineOptions" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  padding: 1.5rem;
}

.chart-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.chart-wrapper {
  height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
