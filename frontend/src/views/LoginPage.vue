<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'
import { useHead } from '@unhead/vue'
import { useRoute } from 'vue-router'

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

const selectedRole = ref('advisor')

const roles = [
  { value: 'student', label: 'Aluno (Estudante)' },
  { value: 'advisor', label: 'Orientador (Professor)' },
  { value: 'coordinator', label: 'Coordenador' },
  { value: 'admin', label: 'Administrador' }
]

const handleLogin = () => {
  authStore.login(selectedRole.value)
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
        </p>
      </div>

      <!-- Seletor de Perfil no Modo Demo -->
      <div class="role-selector-wrapper">
        <label class="role-selector-label">Selecione o perfil de acesso (Modo Demo)</label>
        <div class="role-options">
          <button 
            v-for="opt in roles" 
            :key="opt.value" 
            type="button" 
            class="role-opt-btn"
            :class="{ active: selectedRole === opt.value }"
            @click="selectedRole = opt.value"
          >
            <span class="role-opt-icon">
              <!-- Graduation Cap for Student -->
              <svg v-if="opt.value === 'student'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
              </svg>
              <!-- Academic Board/Advisor -->
              <svg v-else-if="opt.value === 'advisor'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
              </svg>
              <!-- Briefcase for Coordinator -->
              <svg v-else-if="opt.value === 'coordinator'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <!-- Cog Wheel for Admin -->
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </span>
            <span class="role-opt-title">{{ opt.label }}</span>
          </button>
        </div>
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

/* Estilos do Seletor de Perfil */
.role-selector-wrapper {
  width: 100%;
  margin-bottom: 2rem;
  text-align: left;
}

.role-selector-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  letter-spacing: 0.05em;
  text-align: center;
}

.role-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.role-opt-btn {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 0.75rem;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  transition: var(--transition-fast);
}

.role-opt-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.role-opt-btn.active {
  background: rgba(99, 102, 241, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.role-opt-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-opt-icon svg {
  width: 20px;
  height: 20px;
}

.role-opt-title {
  font-size: 0.8rem;
  font-weight: 600;
}
</style>
