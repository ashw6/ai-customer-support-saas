import { Bot, UserRound } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { ChatMessage } from '@/types/api'
import { SourceCitations } from './SourceCitations'

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === 'user'
  const Icon = isUser ? UserRound : Bot

  return (
    <div className={cn('flex gap-3', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser ? (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <Icon className="h-4 w-4" />
        </div>
      ) : null}
      <div
        className={cn(
          'max-w-[min(720px,86%)] rounded-lg px-4 py-3 text-sm leading-6 shadow-sm',
          isUser ? 'bg-primary text-primary-foreground' : 'border border-border bg-background',
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        {!isUser ? <SourceCitations content={message.content} /> : null}
        <p className={cn('mt-2 text-xs', isUser ? 'text-primary-foreground/70' : 'text-muted-foreground')}>
          {new Date(message.created_at).toLocaleString()}
        </p>
      </div>
      {isUser ? (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <Icon className="h-4 w-4" />
        </div>
      ) : null}
    </div>
  )
}
