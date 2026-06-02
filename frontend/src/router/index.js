import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Lazy loading views for better performance
const LoginPage = () => import('../views/LoginPage.vue')
const DashboardPage = () => import('../views/DashboardPage.vue')
const ProjectsPage = () => import('../views/ProjectsPage.vue')
const ProjectDetailPage = () => import('../views/ProjectDetailPage.vue')
const SubmissionsPage = () => import('../views/SubmissionsPage.vue')
const MainLayout = () => import('../layouts/MainLayout.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardPage
      },
      {
        path: 'projects',
        name: 'Projects',
        component: ProjectsPage
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: ProjectDetailPage
      },
      {
        path: 'projects/:id/submissions',
        name: 'Submissions',
        component: SubmissionsPage
      }
    ]
  },
  // Redirect any unknown path to home
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // If store is in initial loading state, fetch user status once
  if (authStore.loading) {
    await authStore.fetchUser()
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
