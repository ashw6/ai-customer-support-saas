import { useEffect, useRef } from 'react'
import { Bot } from 'lucide-react'
import { EmptyState } from '@/components/EmptyState'
import type { ChatMessage } from '@/types/api'
import { ChatInput } from './ChatInput'
import { MessageBubble } from './MessageBubble'

interface ChatWindowProps {
  conversationId: number | null
  messages: ChatMessage[]
  draft: string
  sending?: boolean
  readOnly?: boolean
  readOnlyReason?: string
  onDraftChange: (value: string) => void
  onSend: () => void
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
        <Bot className="h-4 w-4" />
      </div>
      <div className="rounded-lg border border-border bg-background px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.2s]" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.1s]" />
          <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
        </div>
      </div>
    </div>
  )
}

export function ChatWindow({
  conversationId,
  messages,
  draft,
  sending = false,
  readOnly = false,
  readOnlyReason,
  onDraftChange,
  onSend,
}: ChatWindowProps) {
  const endRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  return (
    <section className="flex min-h-[calc(100vh-11rem)] flex-col rounded-lg border border-border bg-card shadow-sm">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold">
          {conversationId ? `Conversation #${conversationId}` : 'New conversation'}
        </h2>
        <p className="mt-1 text-xs text-muted-foreground">
          {sending
            ? 'Generating a reply. AI responses can take up to a minute. Keep this tab open.'
            : 'Responses use indexed documents when available. Ensure the API and AI provider are configured.'}
        </p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <EmptyState
            title="Ask the assistant"
            description="Start with a customer issue, policy question, billing concern, or account workflow."
            className="min-h-[420px]"
          />
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}
        {sending ? <TypingIndicator /> : null}
        <div ref={endRef} />
      </div>

      {readOnly && readOnlyReason ? (
        <div className="border-t border-border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
          {readOnlyReason}
        </div>
      ) : null}
      <ChatInput
        value={draft}
        disabled={sending || readOnly}
        onChange={onDraftChange}
        onSubmit={onSend}
      />
    </section>
  )
}
