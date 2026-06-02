<script setup>
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()

const handleLogin = () => {
  authStore.login()
}
</script>

<template>
  <div class="login-container">
    <!-- Animated background glowing orbs -->
    <div class="glow-orb orb-1"></div>
    <div class="glow-orb orb-2"></div>
    
    <div class="login-card glass-card">
      <div class="brand-section">
        <div class="logo-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="logo-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h1 class="brand-name">IFAL <span class="text-gradient">Projetos</span></h1>
        <p class="brand-tagline">Plataforma Integrada de Gestão de Projetos Acadêmicos</p>
      </div>

      <div class="info-section">
        <p class="info-text">
          Acesse a plataforma utilizando suas credenciais institucionais do SUAP. 
          Alunos, orientadores e administradores têm acesso unificado.
        </p>
      </div>

      <button class="btn btn-primary login-btn" @click="handleLogin">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="suap-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Entrar com SUAP
      </button>

      <div class="footer-links">
        <a href="https://suap.ifal.edu.br" target="_blank" rel="noopener" class="footer-link">Esqueceu as credenciais? Acesse o SUAP</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-primary);
  position: relative;
  overflow: hidden;
  padding: 1.5rem;
}

/* Glowing background orbs */
.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.15;
  z-index: 1;
  pointer-events: none;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: var(--color-primary);
  top: -100px;
  left: -100px;
  animation: float-1 20s infinite ease-in-out;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: var(--color-secondary);
  bottom: -150px;
  right: -150px;
  animation: float-2 25s infinite ease-in-out;
}

@keyframes float-1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(50px, 30px) scale(1.1); }
}

@keyframes float-2 {
  0%, 100% { transform: translate(0, 0) scale(1.1); }
  50% { transform: translate(-60px, -40px) scale(0.9); }
}

.login-card {
  width: 100%;
  max-width: 450px;
  padding: 3rem 2.5rem;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.brand-section {
  margin-bottom: 2rem;
}

.logo-wrapper {
  width: 64px;
  height: 64px;
  background: var(--gradient-primary);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem auto;
  box-shadow: 0 8px 24px 0 rgba(99, 102, 241, 0.3);
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: #ffffff;
}

.brand-name {
  font-family: 'Outfit', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.brand-tagline {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.info-section {
  margin-bottom: 2.5rem;
  border-top: 1px solid var(--border-glass);
  border-bottom: 1px solid var(--border-glass);
  padding: 1.5rem 0;
}

.info-text {
  font-size: 0.875rem;
  color: var(--text-muted);
  line-height: 1.6;
}

.login-btn {
  width: 100%;
  padding: 0.875rem;
  font-size: 1rem;
  box-shadow: 0 8px 20px 0 rgba(99, 102, 241, 0.4);
}

.suap-icon {
  width: 20px;
  height: 20px;
}

.footer-links {
  margin-top: 2rem;
}

.footer-link {
  font-size: 0.75rem;
  color: var(--text-muted);
  transition: var(--transition-fast);
}

.footer-link:hover {
  color: var(--color-primary);
}
</style>
