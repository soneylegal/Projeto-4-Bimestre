import { useNotificationStore } from '../store/notifications'
import { apiUrl } from './api'

let eventSource = null

export function connectSSE() {
  const notify = useNotificationStore()

  if (eventSource) {
    eventSource.close()
  }

  eventSource = new EventSource(apiUrl('/api/notifications/stream'), {
    withCredentials: true
  })

  eventSource.addEventListener('notification', (event) => {
    try {
      const data = JSON.parse(event.data)
      notify.add(data.message, data.type || 'info')
    } catch (e) {
      console.error('Erro ao processar notificação SSE:', e)
    }
  })

  eventSource.onerror = () => {
    console.warn('SSE connection error, will reconnect...')
  }
}

export function disconnectSSE() {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
}
