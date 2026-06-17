import { defineStore } from 'pinia'
import { apiFetch, apiUrl } from '@/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: true,
  }),
  
  actions: {
    async fetchUser() {
      this.loading = true
      try {
        const response = await apiFetch('/api/auth/me', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.user = data
          this.isAuthenticated = true
        } else {
          // If 401/unauthorized, clear state
          this.clearAuth()
        }
      } catch (error) {
        console.error('Erro ao buscar dados do usuário:', error)
        this.clearAuth()
      } finally {
        this.loading = false
      }
    },
    
    async logout() {
      this.loading = true
      try {
        const response = await apiFetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
          }
        })
        if (response.ok) {
          this.clearAuth()
          // Redirect to login page
          window.location.href = '/login'
        } else {
          console.error('Falha ao efetuar logout')
        }
      } catch (error) {
        console.error('Erro ao efetuar logout:', error)
      } finally {
        this.loading = false
      }
    },
    
    login() {
      // Direct redirection to the FastAPI authorize endpoint
      window.location.href = apiUrl('/api/auth/authorize')
    },
    
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
    }
  }
})
