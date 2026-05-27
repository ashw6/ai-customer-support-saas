import { MessageCircle, Plus } from 'lucide-react'
import { EmptyState } from '@/components/EmptyState'
import { cn } from '@/lib/utils'
import type { ConversationSummary } from '@/types/api'

interface ConversationSidebarProps {
  conversations: ConversationSummary[]
  activeId: number | null
  disabled?: boolean
  onSelect: (id: number) => void
  onNew: () => void
}

export function ConversationSidebar({
  conversations,
  activeId,
  disabled = false,
  onSelect,
  onNew,
}: ConversationSidebarProps) {
  return (
    <aside className="rounded-lg border border-border bg-card p-4 shadow-sm lg:max-h-[calc(100vh-8rem)] lg:overflow-y-auto">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold">Conversations</h2>
        <button
          type="button"
          onClick={onNew}
          disabled={disabled}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <Plus className="h-4 w-4" />
          New
        </button>
      </div>
      <div className="mt-4 space-y-2">
        {conversations.length === 0 ? (
          <EmptyState title="No conversations" description="Start a chat to create your first thread." />
        ) : (
          conversations.map((conversation) => (
            <button
              key={conversation.id}
              type="button"
              onClick={() => onSelect(conversation.id)}
              disabled={disabled}
              className={cn(
                'flex w-full items-start gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                conversation.id === activeId
                  ? 'bg-primary text-primary-foreground'
                  : 'text-foreground hover:bg-muted',
                disabled ? 'cursor-not-allowed opacity-70' : '',
              )}
            >
              <MessageCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span className="line-clamp-2">{conversation.title}</span>
            </button>
          ))
        )}
      </div>
    </aside>
  )
}
