import { BookOpen } from 'lucide-react'

interface SourceCitationsProps {
  content: string
}

export function extractSourceLabels(content: string): string[] {
  const matches = content.match(/\[Source\s+\d+[^\]]*\]/gi) ?? []
  return Array.from(new Set(matches.map((match) => match.replace(/^\[|\]$/g, ''))))
}

export function SourceCitations({ content }: SourceCitationsProps) {
  const sources = extractSourceLabels(content)
  if (sources.length === 0) return null

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {sources.map((source) => (
        <span
          key={source}
          className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/60 px-2.5 py-1 text-xs font-medium text-muted-foreground"
        >
          <BookOpen className="h-3 w-3" />
          {source}
        </span>
      ))}
    </div>
  )
}
