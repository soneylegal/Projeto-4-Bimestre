import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../../store/auth'
import SidebarNav from '../SidebarNav.vue'

vi.mock('vue-router', () => ({
  useRoute: () => ({ path: '/dashboard' }),
  useRouter: () => ({ push: vi.fn() }),
}))

const createWrapper = (role, pinia) => {
  const store = useAuthStore()
  store.user = { role }

  return mount(SidebarNav, {
    global: {
      plugins: [pinia],
      stubs: {
        'router-link': {
          props: ['to'],
          template: '<a :href="to" class="menu-item"><slot/></a>'
        },
        'router-view': true
      }
    }
  })
}

describe('SidebarNav', () => {
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('admin sees 4 menu items (Projetos, Administração, Relatórios, Avaliações)', () => {
    const wrapper = createWrapper('admin', pinia)
    const items = wrapper.findAll('.menu-item')
    expect(items.length).toBe(4)
  })

  it('coordinator sees 4 menu items (Dashboard, Projetos, Relatórios, Avaliações)', () => {
    const wrapper = createWrapper('coordinator', pinia)
    const items = wrapper.findAll('.menu-item')
    expect(items.length).toBe(4)
  })

  it('advisor sees 3 menu items (Dashboard, Projetos, Avaliações)', () => {
    const wrapper = createWrapper('advisor', pinia)
    const items = wrapper.findAll('.menu-item')
    expect(items.length).toBe(3)
  })

  it('student sees 2 menu items (Projetos, Meus Projetos)', () => {
    const wrapper = createWrapper('student', pinia)
    const items = wrapper.findAll('.menu-item')
    expect(items.length).toBe(2)
  })

  it('admin has Administração link', () => {
    const wrapper = createWrapper('admin', pinia)
    const links = wrapper.findAll('a')
    const texts = links.map(l => l.text())
    expect(texts).toContain('Administração')
  })

  it('student does not have Dashboard link', () => {
    const wrapper = createWrapper('student', pinia)
    const links = wrapper.findAll('a')
    const texts = links.map(l => l.text())
    expect(texts).not.toContain('Dashboard')
  })

  it('student has Meus Projetos link', () => {
    const wrapper = createWrapper('student', pinia)
    const links = wrapper.findAll('a')
    const texts = links.map(l => l.text())
    expect(texts).toContain('Meus Projetos')
  })

  it('advisor has Dashboard link', () => {
    const wrapper = createWrapper('advisor', pinia)
    const links = wrapper.findAll('a')
    const texts = links.map(l => l.text())
    expect(texts).toContain('Dashboard')
  })
})
