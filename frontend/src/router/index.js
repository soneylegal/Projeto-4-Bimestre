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
    meta: { 
      requiresAuth: false,
      title: 'Login | IFAL Projetos',
      description: 'Acesse a plataforma de gestão de projetos acadêmicos do IFAL com suas credenciais SUAP.'
    }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardPage,
        meta: {
          title: 'Dashboard | IFAL Projetos',
          description: 'Painel de controle com visão geral de projetos, tarefas e submissões acadêmicas.'
        }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: ProjectsPage,
        meta: {
          title: 'Projetos | IFAL Projetos',
          description: 'Gerencie e visualize todos os projetos acadêmicos vinculados à sua conta.'
        }
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: ProjectDetailPage,
        meta: {
          title: 'Detalhes do Projeto | IFAL Projetos',
          description: 'Visualize detalhes, equipe e quadro Kanban do projeto acadêmico.'
        }
      },
      {
        path: 'projects/:id/submissions',
        name: 'Submissions',
        component: SubmissionsPage,
        meta: {
          title: 'Submissões | IFAL Projetos',
          description: 'Histórico de submissões e entregas de arquivos do projeto acadêmico.'
        }
      }
    ]
  },
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
