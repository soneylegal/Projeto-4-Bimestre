/**
 * Helper para chamadas à API do backend.
 *
 * Em desenvolvimento (Vite dev server), VITE_API_BASE_URL é vazia e as
 * requisições usam caminhos relativos (ex: '/api/projects'), aproveitando
 * o proxy configurado no vite.config.js.
 *
 * Em produção (Render), VITE_API_BASE_URL contém a URL completa do backend
 * (ex: 'https://ifal-projetos-backend.onrender.com'), e as requisições
 * são direcionadas diretamente ao serviço remoto.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * Constrói a URL completa para um endpoint da API.
 * @param {string} path - Caminho do endpoint (ex: '/api/projects')
 * @returns {string} URL completa
 */
export function apiUrl(path) {
  return `${API_BASE_URL}${path}`
}

/**
 * Wrapper do fetch nativo com prefixo automático da URL base.
 * Uso: import { apiFetch } from '@/utils/api'
 *      const res = await apiFetch('/api/projects', { method: 'GET' })
 *
 * @param {string} path - Caminho do endpoint (ex: '/api/projects')
 * @param {RequestInit} options - Opções padrão do fetch
 * @returns {Promise<Response>}
 */
export async function apiFetch(path, options = {}) {
  const url = apiUrl(path)

  const defaultOptions = {
    credentials: 'include',
    ...options,
  }

  return fetch(url, defaultOptions)
}

export async function apiFetchWithTimeout(path, options = {}, timeoutMs = 10000) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const url = apiUrl(path)
    const defaultOptions = {
      credentials: 'include',
      signal: controller.signal,
      ...options,
    }
    return await fetch(url, defaultOptions)
  } finally {
    clearTimeout(timeoutId)
  }
}
