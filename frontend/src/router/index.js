import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

// Lazy loading views for better performance
const LoginPage = () => import('../views/LoginPage.vue')
const DashboardPage = () => import('../views/DashboardPage.vue')
const ProjectsPage = () => import('../views/ProjectsPage.vue')
const ProjectDetailPage = () => import('../views/ProjectDetailPage.vue')
const SubmissionsPage = () => import('../views/SubmissionsPage.vue')
const MainLayout = () => import('../layouts/MainLayout.vue')
const UsersPage = () => import('../views/admin/UsersPage.vue')
const AuditLogPage = () => import('../views/admin/AuditLogPage.vue')
const SettingsPage = () => import('../views/admin/SettingsPage.vue')
const MyProjectsPage = () => import('../views/student/MyProjectsPage.vue')
const PendingEvaluationsPage = () => import('../views/evaluator/PendingEvaluationsPage.vue')

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
      },
      {
        path: 'admin',
        component: () => import('../layouts/AdminLayout.vue'),
        meta: { role: 'admin', title: 'Administração | IFAL Projetos' },
        children: [
          {
            path: '',
            name: 'AdminUsers',
            component: UsersPage,
            meta: { title: 'Usuários | IFAL Projetos' }
          },
          {
            path: 'logs',
            name: 'AdminLogs',
            component: AuditLogPage,
            meta: { title: 'Auditoria | IFAL Projetos' }
          },
          {
            path: 'settings',
            name: 'AdminSettings',
            component: SettingsPage,
            meta: { title: 'Configurações | IFAL Projetos' }
          }
        ]
      },
      {
        path: 'meus-projetos',
        name: 'MyProjects',
        component: MyProjectsPage,
        meta: {
          role: 'student',
          title: 'Meus Projetos | IFAL Projetos',
          description: 'Acompanhe seus projetos e entregas acadêmicas.'
        }
      },
      {
        path: 'pendentes',
        name: 'PendingEvaluations',
        component: PendingEvaluationsPage,
        meta: {
          role: ['advisor', 'coordinator', 'admin'],
          title: 'Avaliações Pendentes | IFAL Projetos',
          description: 'Gerencie as submissões pendentes de avaliação.'
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

const roleRoots = {
  admin: '/admin',
  coordinator: '/',
  advisor: '/',
  student: '/meus-projetos'
}

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (authStore.loading) {
    await authStore.fetchUser()
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  if (to.path === '/login' && authStore.isAuthenticated) {
    next(roleRoots[authStore.role] || '/')
    return
  }

  if (to.path === '/' && authStore.isAuthenticated) {
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

export default router
