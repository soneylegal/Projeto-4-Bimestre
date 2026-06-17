<script setup>
import { useNotificationStore } from '../store/notifications'

const notificationStore = useNotificationStore()
</script>

<template>
  <div class="toast-container">
    <transition-group name="toast-slide" tag="div" class="toast-wrapper">
      <div 
        v-for="toast in notificationStore.notifications" 
        :key="toast.id" 
        class="toast-item glass-card"
        :class="toast.type"
      >
        <div class="toast-icon-wrapper">
          <!-- Success Icon -->
          <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="toast-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <!-- Error Icon -->
          <svg v-else-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="toast-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <!-- Warning Icon -->
          <svg v-else-if="toast.type === 'warning'" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="toast-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <!-- Info Icon -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="toast-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <div class="toast-message">
          {{ toast.message }}
        </div>

        <button class="toast-close-btn" @click="notificationStore.remove(toast.id)" title="Fechar">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="close-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  pointer-events: none;
  max-width: 400px;
  width: calc(100% - 3rem);
}

.toast-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  border-radius: var(--radius-md);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  border-left: 4px solid var(--color-primary);
  background: rgba(30, 41, 59, 0.85); /* fallback escuro para contraste */
}

/* Color types modifiers */
.toast-item.success {
  border-left-color: var(--color-success);
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-left: 4px solid var(--color-success);
}
.toast-item.success .toast-icon {
  color: var(--color-success);
}

.toast-item.error {
  border-left-color: var(--color-danger);
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-left: 4px solid var(--color-danger);
}
.toast-item.error .toast-icon {
  color: var(--color-danger);
}

.toast-item.warning {
  border-left-color: var(--color-warning);
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.15);
  border-left: 4px solid var(--color-warning);
}
.toast-item.warning .toast-icon {
  color: var(--color-warning);
}

.toast-item.info {
  border-left-color: var(--color-info);
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-left: 4px solid var(--color-info);
}
.toast-item.info .toast-icon {
  color: var(--color-info);
}

.toast-icon-wrapper {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-icon {
  width: 20px;
  height: 20px;
}

.toast-message {
  flex-grow: 1;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
}

.toast-close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.toast-close-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.close-icon {
  width: 14px;
  height: 14px;
}

/* Slide Transition */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.95);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(50px) scale(0.95);
}
</style>
