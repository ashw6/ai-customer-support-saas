import { FileText, Loader2, Trash2 } from 'lucide-react'
import { EmptyState } from '@/components/EmptyState'
import type { KnowledgeDocument } from '@/types/api'

interface DocumentTableProps {
  documents: KnowledgeDocument[]
  deletingId?: number | null
  onDelete: (document: KnowledgeDocument) => void
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  const units = ['KB', 'MB', 'GB']
  let value = bytes / 1024
  let unitIndex = 0
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[unitIndex]}`
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

export function DocumentTable({ documents, deletingId = null, onDelete }: DocumentTableProps) {
  if (documents.length === 0) {
    return (
      <EmptyState
        title="No documents uploaded"
        description="Add a PDF to make its content available to grounded AI responses."
      />
    )
  }

  return (
    <section className="rounded-lg border border-border bg-card shadow-sm">
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-sm font-semibold">Indexed documents</h2>
      </div>

      <div className="hidden overflow-x-auto md:block">
        <table className="min-w-full divide-y divide-border text-sm">
          <thead className="bg-muted/40 text-left text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-5 py-3 font-semibold">Document</th>
              <th className="px-5 py-3 font-semibold">Size</th>
              <th className="px-5 py-3 font-semibold">Chunks</th>
              <th className="px-5 py-3 font-semibold">Text</th>
              <th className="px-5 py-3 font-semibold">Uploaded</th>
              <th className="px-5 py-3 text-right font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {documents.map((document) => {
              const deleting = deletingId === document.id
              return (
                <tr key={document.id} className="bg-card">
                  <td className="px-5 py-4">
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="truncate font-medium text-foreground">{document.filename}</p>
                        <p className="text-xs text-muted-foreground">{document.content_type}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-muted-foreground">{formatBytes(document.file_size)}</td>
                  <td className="px-5 py-4 text-muted-foreground">{document.chunk_count}</td>
                  <td className="px-5 py-4 text-muted-foreground">{document.text_length.toLocaleString()}</td>
                  <td className="px-5 py-4 text-muted-foreground">{formatDate(document.created_at)}</td>
                  <td className="px-5 py-4 text-right">
                    <button
                      type="button"
                      onClick={() => onDelete(document)}
                      disabled={deleting}
                      className="inline-flex items-center justify-center rounded-md p-2 text-muted-foreground hover:bg-destructive/10 hover:text-destructive disabled:cursor-not-allowed disabled:opacity-50"
                      aria-label={`Delete ${document.filename}`}
                      title="Delete document"
                    >
                      {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="divide-y divide-border md:hidden">
        {documents.map((document) => {
          const deleting = deletingId === document.id
          return (
            <article key={document.id} className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                  <FileText className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="break-words text-sm font-semibold">{document.filename}</h3>
                  <p className="mt-1 text-xs text-muted-foreground">{formatDate(document.created_at)}</p>
                </div>
                <button
                  type="button"
                  onClick={() => onDelete(document)}
                  disabled={deleting}
                  className="rounded-md p-2 text-muted-foreground hover:bg-destructive/10 hover:text-destructive disabled:cursor-not-allowed disabled:opacity-50"
                  aria-label={`Delete ${document.filename}`}
                >
                  {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                </button>
              </div>
              <dl className="mt-4 grid grid-cols-3 gap-3 text-xs">
                <div>
                  <dt className="text-muted-foreground">Size</dt>
                  <dd className="mt-1 font-medium">{formatBytes(document.file_size)}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Chunks</dt>
                  <dd className="mt-1 font-medium">{document.chunk_count}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Text</dt>
                  <dd className="mt-1 font-medium">{document.text_length.toLocaleString()}</dd>
                </div>
              </dl>
            </article>
          )
        })}
      </div>
    </section>
  )
}
