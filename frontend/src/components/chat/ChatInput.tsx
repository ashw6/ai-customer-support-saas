import { type FormEvent } from 'react'
import { Loader2, Send } from 'lucide-react'

interface ChatInputProps {
  value: string
  disabled?: boolean
  onChange: (value: string) => void
  onSubmit: () => void
}

export function ChatInput({ value, disabled = false, onChange, onSubmit }: ChatInputProps) {
  const trimmed = value.trim()

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!trimmed || disabled) return
    onSubmit()
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-border bg-card p-4">
      <div className="flex flex-col gap-3 sm:flex-row">
        <label className="sr-only" htmlFor="chat-message">
          Message
        </label>
        <textarea
          id="chat-message"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              if (trimmed && !disabled) onSubmit()
            }
          }}
          placeholder="Ask about policies, orders, billing, support workflows..."
          rows={2}
          disabled={disabled}
          className="min-h-[52px] flex-1 resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none disabled:cursor-not-allowed disabled:opacity-70 focus-visible:ring-2 focus-visible:ring-ring"
        />
        <button
          type="submit"
          disabled={disabled || !trimmed}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {disabled ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          {disabled ? 'Thinking' : 'Send'}
        </button>
      </div>
    </form>
  )
}
