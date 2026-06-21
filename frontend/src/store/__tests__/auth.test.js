import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'

describe('authStore getters', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('isAdmin returns true when role is admin', () => {
    const store = useAuthStore()
    store.user = { role: 'admin' }
    expect(store.isAdmin).toBe(true)
    expect(store.isCoordinator).toBe(false)
    expect(store.isAdvisor).toBe(false)
    expect(store.isStudent).toBe(false)
  })

  it('isCoordinator returns true when role is coordinator', () => {
    const store = useAuthStore()
    store.user = { role: 'coordinator' }
    expect(store.isCoordinator).toBe(true)
    expect(store.isAdmin).toBe(false)
    expect(store.isAdvisor).toBe(false)
    expect(store.isStudent).toBe(false)
  })

  it('isAdvisor returns true when role is advisor', () => {
    const store = useAuthStore()
    store.user = { role: 'advisor' }
    expect(store.isAdvisor).toBe(true)
    expect(store.isAdmin).toBe(false)
    expect(store.isCoordinator).toBe(false)
    expect(store.isStudent).toBe(false)
  })

  it('isStudent returns true when role is student', () => {
    const store = useAuthStore()
    store.user = { role: 'student' }
    expect(store.isStudent).toBe(true)
    expect(store.isAdmin).toBe(false)
    expect(store.isCoordinator).toBe(false)
    expect(store.isAdvisor).toBe(false)
  })

  it('all getters return false when user is null', () => {
    const store = useAuthStore()
    store.user = null
    expect(store.isAdmin).toBe(false)
    expect(store.isCoordinator).toBe(false)
    expect(store.isAdvisor).toBe(false)
    expect(store.isStudent).toBe(false)
    expect(store.role).toBeNull()
  })

  it('can() checks role hierarchy correctly', () => {
    const store = useAuthStore()
    store.user = { role: 'coordinator' }
    expect(store.can('student')).toBe(true)
    expect(store.can('advisor')).toBe(true)
    expect(store.can('coordinator')).toBe(true)
    expect(store.can('admin')).toBe(false)
  })

  it('can() returns false for null user', () => {
    const store = useAuthStore()
    store.user = null
    expect(store.can('student')).toBe(false)
  })
})
