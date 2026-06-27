<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { apiFetch } from '../utils/api'
import { useAuthStore } from '../store/auth'

const props = defineProps({
  projectId: { type: String, required: true }
})

const authStore = useAuthStore()
const messages = ref([])
const newMessage = ref('')
const loading = ref(true)
const ws = ref(null)
const chatRef = ref(null)

function getWebSocketUrl() {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const base = import.meta.env.VITE_API_BASE_URL || ''
  if (base) {
    const host = base.replace(/^https?:\/\//, '')
    return `${proto}//${host}/ws/chat/${props.projectId}`
  }
  return `${proto}//${window.location.host}/ws/chat/${props.projectId}`
}

onMounted(async () => {
  try {
    const res = await apiFetch(`/api/projects/${props.projectId}/messages`, { method: 'GET' })
    if (res.ok) {
      messages.value = await res.json()
    }
  } catch (e) {
    console.error('Erro ao carregar mensagens:', e)
  } finally {
    loading.value = false
  }

  // Connect WebSocket
  try {
    ws.value = new WebSocket(getWebSocketUrl())
    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        messages.value.push(data)
        scrollToBottom()
      } catch {
        // ignore non-JSON messages
      }
    }
  } catch (e) {
    console.error('Erro ao conectar WebSocket:', e)
  }
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})

async function send() {
  const text = newMessage.value.trim()
  if (!text) return

  try {
    const res = await apiFetch(`/api/projects/${props.projectId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text })
    })
    if (res.ok) {
      const msg = await res.json()
      messages.value.push(msg)
      newMessage.value = ''
      scrollToBottom()

      // Send via WebSocket
      if (ws.value && ws.value.readyState === WebSocket.OPEN) {
        ws.value.send(JSON.stringify(msg))
      }
    }
  } catch (e) {
    console.error('Erro ao enviar mensagem:', e)
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatRef.value) {
      chatRef.value.scrollTop = chatRef.value.scrollHeight
    }
  })
}
</script>

<template>
  <div class="chat-widget glass-card">
    <div class="chat-header">
      <h3>Chat do Projeto</h3>
    </div>

    <div ref="chatRef" class="chat-messages" v-if="!loading">
      <div v-if="messages.length === 0" class="empty-chat">
        Nenhuma mensagem ainda. Inicie a conversa!
      </div>
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message"
        :class="{ mine: msg.sender_id === authStore.user?.id }"
      >
        <div class="message-sender">{{ msg.sender_name || 'Desconhecido' }}</div>
        <div class="message-content">{{ msg.content }}</div>
        <div class="message-time">{{ new Date(msg.created_at).toLocaleTimeString('pt-BR') }}</div>
      </div>
    </div>

    <div v-else class="loading-msg">Carregando...</div>

    <form @submit.prevent="send" class="chat-input">
      <input
        v-model="newMessage"
        type="text"
        placeholder="Digite sua mensagem..."
        class="form-input"
      />
      <button type="submit" class="btn btn-primary btn-sm">Enviar</button>
    </form>
  </div>
</template>

<style scoped>
.chat-widget {
  display: flex;
  flex-direction: column;
  height: 400px;
  padding: 0;
  overflow: hidden;
}

.chat-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-glass);
}

.chat-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.empty-chat {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
  font-size: 0.875rem;
}

.loading-msg {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}

.message {
  max-width: 80%;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  background: var(--bg-tertiary);
  align-self: flex-start;
}

.message.mine {
  background: rgba(44, 103, 205, 0.15);
  align-self: flex-end;
}

.message-sender {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.2rem;
}

.message.mine .message-sender {
  color: var(--color-primary);
}

.message-content {
  font-size: 0.85rem;
  color: var(--text-primary);
}

.message-time {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
  text-align: right;
}

.chat-input {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-glass);
}

.chat-input .form-input {
  flex: 1;
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.chat-input .form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}
</style>
