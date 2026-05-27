import { useEffect, useMemo, useState } from 'react'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { ConversationSidebar } from '@/components/chat/ConversationSidebar'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { LeadCaptureModal } from '@/components/LeadCaptureModal'
import { SkeletonBlock } from '@/components/LoadingState'
import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import {
  adminNav,
  customerNav,
  DashboardLayout,
  supportNav,
  type NavItem,
} from '@/layouts/DashboardLayout'
import { parseApiError } from '@/services/api'
import { fetchChatHistory, fetchConversation, sendChatMessage } from '@/services/chat.service'
import type { ChatMessage, ConversationSummary } from '@/types/api'

const LEAD_KEYWORDS = [
  'pricing',
  'price',
  'demo',
  'trial',
  'buy',
  'purchase',
  'quote',
  'sales',
  'subscribe',
  'subscription',
  'upgrade',
  'book a call',
  'contact sales',
]

function navForRole(role: string | undefined): NavItem[] {
  if (role === 'admin') return adminNav
  if (role === 'support_agent') return supportNav
  return customerNav
}

function ChatSkeleton() {
  return (
    <div className="grid gap-4 lg:grid-cols-[300px_minmax(0,1fr)]">
      <div className="rounded-lg border border-border bg-card p-4">
        <SkeletonBlock className="h-5 w-32" />
        <SkeletonBlock className="mt-4 h-12 w-full" />
        <SkeletonBlock className="mt-3 h-12 w-full" />
      </div>
      <div className="rounded-lg border border-border bg-card p-4">
        <SkeletonBlock className="h-5 w-40" />
        <SkeletonBlock className="mt-6 h-14 w-4/5" />
        <SkeletonBlock className="ml-auto mt-4 h-14 w-3/5" />
        <SkeletonBlock className="mt-4 h-14 w-2/3" />
      </div>
    </div>
  )
}

function optimisticMessage(content: string, conversationId: number | null): ChatMessage {
  return {
    id: -Date.now(),
    conversation_id: conversationId ?? 0,
    sender: 'user',
    content,
    created_at: new Date().toISOString(),
  }
}

function detectLeadInterest(message: string): string | null {
  const normalized = ` ${message.toLowerCase()} `
  return LEAD_KEYWORDS.find((keyword) => normalized.includes(keyword)) ?? null
}

function pickInitialConversation(
  rows: ConversationSummary[],
  userId: number | undefined,
): ConversationSummary | null {
  if (!rows.length || userId == null) return rows[0] ?? null
  return rows.find((row) => row.user_id === userId) ?? null
}

function canSendInConversation(
  conversationId: number | null,
  history: ConversationSummary[],
  userId: number | undefined,
): boolean {
  if (conversationId == null) return true
  if (userId == null) return false
  const conversation = history.find((row) => row.id === conversationId)
  return !conversation || conversation.user_id === userId
}

export function ChatPage() {
  const { user } = useAuth()
  const toast = useToast()
  const [history, setHistory] = useState<ConversationSummary[]>([])
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [leadPrompt, setLeadPrompt] = useState<{ keyword: string; message: string } | null>(null)
  const [leadDismissed, setLeadDismissed] = useState(false)
  const navItems = useMemo(() => navForRole(user?.role), [user?.role])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError('')
      try {
        const rows = await fetchChatHistory()
        if (cancelled) return
        setHistory(rows)
        const initial = pickInitialConversation(rows, user?.id)
        if (initial) {
          const detail = await fetchConversation(initial.id)
          if (!cancelled) {
            setConversationId(detail.id)
            setMessages(detail.messages)
          }
        }
      } catch (err) {
        const message = parseApiError(err)
        if (!cancelled) {
          setError(message)
          toast.error('Could not load chat', message)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [toast, user?.id])

  const selectConversation = async (id: number) => {
    if (sending || id === conversationId) return
    setLoading(true)
    setError('')
    try {
      const detail = await fetchConversation(id)
      setConversationId(detail.id)
      setMessages(detail.messages)
    } catch (err) {
      const message = parseApiError(err)
      setError(message)
      toast.error('Could not open conversation', message)
    } finally {
      setLoading(false)
    }
  }

  const startNewConversation = () => {
    if (sending) return
    setConversationId(null)
    setMessages([])
    setDraft('')
    setError('')
  }

  const canSend = canSendInConversation(conversationId, history, user?.id)

  const handleSend = async () => {
    const content = draft.trim()
    if (!content || sending || !canSend) return

    const pendingMessage = optimisticMessage(content, conversationId)
    const leadKeyword = detectLeadInterest(content)
    setDraft('')
    setSending(true)
    setError('')
    setMessages((current) => [...current, pendingMessage])
    if (leadKeyword && !leadDismissed && !leadPrompt) {
      setLeadPrompt({ keyword: leadKeyword, message: content })
    }

    try {
      const response = await sendChatMessage({
        message: content,
        conversation_id: conversationId ?? undefined,
      })
      setConversationId(response.conversation.id)
      setMessages((current) => [
        ...current.filter((message) => message.id !== pendingMessage.id),
        response.user_message,
        response.ai_message,
      ])
      setHistory((current) => {
        const withoutCurrent = current.filter((item) => item.id !== response.conversation.id)
        return [response.conversation, ...withoutCurrent]
      })
    } catch (err) {
      const message = parseApiError(err)
      setMessages((current) => current.filter((item) => item.id !== pendingMessage.id))
      setDraft(content)
      setError(message)
      toast.error('Message failed', message)
    } finally {
      setSending(false)
    }
  }

  return (
    <DashboardLayout title="AI conversations" subtitle="Chat with the RAG-powered support assistant" navItems={navItems}>
      <ErrorBoundary label="Chat workspace">
        {loading && history.length === 0 ? <ChatSkeleton /> : null}
        {!loading && error ? (
          <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        ) : null}
        <div className="grid gap-4 lg:grid-cols-[300px_minmax(0,1fr)]">
          <ConversationSidebar
            conversations={history}
            activeId={conversationId}
            disabled={sending}
            onSelect={(id) => void selectConversation(id)}
            onNew={startNewConversation}
          />
          <ChatWindow
            conversationId={conversationId}
            messages={messages}
            draft={draft}
            sending={sending}
            readOnly={!canSend}
            readOnlyReason={
              canSend
                ? undefined
                : 'This conversation belongs to another user. Start a new conversation to chat with the assistant.'
            }
            onDraftChange={setDraft}
            onSend={handleSend}
          />
        </div>
        <LeadCaptureModal
          open={leadPrompt !== null}
          user={user}
          matchedKeyword={leadPrompt?.keyword}
          sourceMessage={leadPrompt?.message}
          onClose={() => {
            setLeadDismissed(true)
            setLeadPrompt(null)
          }}
          onCreated={() => {
            setLeadDismissed(true)
            setLeadPrompt(null)
          }}
        />
      </ErrorBoundary>
    </DashboardLayout>
  )
}
