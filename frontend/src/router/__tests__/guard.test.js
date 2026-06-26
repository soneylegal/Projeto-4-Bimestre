import { describe, it, expect, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../../store/auth'

const LoginPage = { template: '<div>Login</div>' }
const DashboardPage = { template: '<div>Dashboard</div>' }
const ProjectsPage = { template: '<div>Projects</div>' }
const ProjectDetailPage = { template: '<div>Detail</div>' }
const SubmissionsPage = { template: '<div>Submissions</div>' }
const MainLayout = { template: '<div><router-view/></div>' }
const MyProjectsPage = { template: '<div>MyProjects</div>' }
const PendingEvaluationsPage = { template: '<div>Pending</div>' }
const ReportsPage = { template: '<div>Reports</div>' }
const UsersPage = { template: '<div>Users</div>' }
const AuditLogPage = { template: '<div>Logs</div>' }
const SettingsPage = { template: '<div>Settings</div>' }
const AdminLayout = { template: '<div><router-view/></div>' }

const routes = [
  { path: '/login', name: 'Login', component: LoginPage, meta: { requiresAuth: false } },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: DashboardPage },
      { path: 'projects', name: 'Projects', component: ProjectsPage },
      { path: 'projects/:id', name: 'ProjectDetail', component: ProjectDetailPage },
      { path: 'projects/:id/submissions', name: 'Submissions', component: SubmissionsPage },
      {
        path: 'admin',
        component: AdminLayout,
        meta: { role: 'admin' },
        children: [
          { path: '', name: 'AdminUsers', component: UsersPage },
          { path: 'logs', name: 'AdminLogs', component: AuditLogPage },
          { path: 'settings', name: 'AdminSettings', component: SettingsPage }
        ]
      },
      { path: 'meus-projetos', name: 'MyProjects', component: MyProjectsPage, meta: { role: 'student' } },
      { path: 'pendentes', name: 'PendingEvaluations', component: PendingEvaluationsPage, meta: { role: ['advisor', 'coordinator', 'admin'] } },
      { path: 'reports', name: 'Reports', component: ReportsPage, meta: { role: ['coordinator', 'admin'] } }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const roleRoots = {
  admin: '/admin',
  coordinator: '/',
  advisor: '/',
  student: '/meus-projetos'
}

function createTestRouter() {
  const router = createRouter({ history: createMemoryHistory(), routes })

  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

    if (requiresAuth && !authStore.isAuthenticated) {
      next('/login')
      return
    }

    if (to.path === '/login' && authStore.isAuthenticated) {
      next(roleRoots[authStore.role] || '/')
      return
    }

    if (to.path === '/' && authStore.isAuthenticated && from.path === '/login') {
      const target = roleRoots[authStore.role]
      if (target !== '/') {
        next(target)
        return
      }
    }

    const requiredRole = to.meta.role
    if (requiredRole) {
      const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole]
      if (!roles.includes(authStore.role)) {
        next(roleRoots[authStore.role] || '/')
        return
      }
    }

    next()
  })

  return router
}

describe('router beforeEach guard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('redirects unauthenticated user to /login', async () => {
    const router = createTestRouter()
    await router.push('/dashboard')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('stays at / for coordinator when clicking Dashboard', async () => {
    const store = useAuthStore()
    store.user = { role: 'coordinator' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.replace('/')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('stays at / for admin when clicking Dashboard', async () => {
    const store = useAuthStore()
    store.user = { role: 'admin' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.replace('/')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('stays at / for student when clicking Dashboard', async () => {
    const store = useAuthStore()
    store.user = { role: 'student' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.replace('/')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('blocks student from accessing /admin', async () => {
    const store = useAuthStore()
    store.user = { role: 'student' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.push('/admin')
    expect(router.currentRoute.value.path).toBe('/meus-projetos')
  })

  it('blocks advisor from accessing /admin', async () => {
    const store = useAuthStore()
    store.user = { role: 'advisor' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.push('/admin')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('allows admin on /admin', async () => {
    const store = useAuthStore()
    store.user = { role: 'admin' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.push('/admin')
    expect(router.currentRoute.value.path).toBe('/admin')
  })

  it('blocks student from accessing /reports', async () => {
    const store = useAuthStore()
    store.user = { role: 'student' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.push('/reports')
    expect(router.currentRoute.value.path).toBe('/meus-projetos')
  })

  it('allows coordinator on /reports', async () => {
    const store = useAuthStore()
    store.user = { role: 'coordinator' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.push('/reports')
    expect(router.currentRoute.value.path).toBe('/reports')
  })

  it('redirects authenticated user away from /login', async () => {
    const store = useAuthStore()
    store.user = { role: 'advisor' }
    store.isAuthenticated = true
    store.loading = false

    const router = createTestRouter()
    await router.push('/login')
    expect(router.currentRoute.value.path).toBe('/')
  })
})
