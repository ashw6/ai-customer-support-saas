import type { ChatSendResponse, ConversationDetail, ConversationSummary } from '@/types/api'
import { api } from './api'

export async function sendChatMessage(payload: {
  message: string
  conversation_id?: number
}): Promise<ChatSendResponse> {
  const chatTimeoutMs = Number(import.meta.env.VITE_CHAT_TIMEOUT_MS ?? 180000)
  const { data } = await api.post<ChatSendResponse>('/chat/send', payload, {
    timeout: Number.isFinite(chatTimeoutMs) && chatTimeoutMs > 0 ? chatTimeoutMs : 180000,
  })
  return data
}

export async function fetchChatHistory(): Promise<ConversationSummary[]> {
  const { data } = await api.get<ConversationSummary[]>('/chat/history')
  return data
}

export async function fetchConversation(id: number): Promise<ConversationDetail> {
  const { data } = await api.get<ConversationDetail>(`/chat/conversation/${id}`)
  return data
}
