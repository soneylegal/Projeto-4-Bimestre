<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'card',
    validator: v => ['card', 'list-item', 'kanban-card', 'stat-card', 'text-block'].includes(v)
  },
  count: {
    type: Number,
    default: 1
  },
  rows: {
    type: Number,
    default: 3
  }
})

const lineWidths = [
  '100%', '85%', '70%', '90%', '75%', '60%', '95%', '80%'
]
</script>

<template>
  <div class="skeleton-card" :class="`variant-${variant}`">
    <div v-for="i in count" :key="i" class="skeleton-item">
      <div v-if="variant === 'stat-card'" class="skeleton-icon" />
      <div class="skeleton-lines">
        <div
          v-for="j in rows"
          :key="j"
          class="skeleton-line"
          :style="{ width: lineWidths[(i + j) % lineWidths.length] }"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
}

.variant-stat-card .skeleton-item {
  flex-direction: row;
  padding: 2rem;
}

.variant-text-block .skeleton-item {
  flex-direction: column;
  align-items: stretch;
  min-height: 120px;
}

.variant-kanban-card .skeleton-item {
  flex-direction: column;
  align-items: stretch;
  min-height: 180px;
}

.variant-list-item .skeleton-item {
  padding: 1rem 1.25rem;
}

.skeleton-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: linear-gradient(90deg, var(--bg-tertiary) 25%, rgba(255,255,255,0.04) 50%, var(--bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  flex-shrink: 0;
}

.skeleton-lines {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  flex: 1;
}

.skeleton-line {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--bg-tertiary) 25%, rgba(255,255,255,0.04) 50%, var(--bg-tertiary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-line:last-child {
  width: 60% !important;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
