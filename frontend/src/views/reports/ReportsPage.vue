<script setup>
</script>

<template>
  <div class="reports-page">
    <h1>Relatórios Institucionais</h1>
    <p class="subtitle">Métricas acadêmicas e relatórios do sistema.</p>

    <div class="report-grid">
      <div class="report-card glass-card">
        <h3>Relatório de Projetos</h3>
        <p>Visão geral de todos os projetos cadastrados no sistema.</p>
        <button class="btn btn-primary" disabled>Em breve</button>
      </div>
      <div class="report-card glass-card">
        <h3>Relatório de Submissões</h3>
        <p>Submissões agrupadas por período e status de avaliação.</p>
        <button class="btn btn-primary" disabled>Em breve</button>
      </div>
      <div class="report-card glass-card">
        <h3>Relatório de Usuários</h3>
        <p>Usuários cadastrados por papel e vínculo institucional.</p>
        <button class="btn btn-primary" disabled>Em breve</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reports-page {
  max-width: 900px;
  margin: 0 auto;
}

.reports-page h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.report-card {
  padding: 1.5rem;
}

.report-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.report-card p {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
</style>
