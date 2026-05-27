import { useEffect, useMemo, useState } from 'react'
import { Database, FileText, Search } from 'lucide-react'
import { DocumentTable } from '@/components/DocumentTable'
import { DocumentUpload } from '@/components/DocumentUpload'
import { LoadingState } from '@/components/LoadingState'
import { useToast } from '@/context/ToastContext'
import { DashboardLayout, adminNav } from '@/layouts/DashboardLayout'
import { parseApiError } from '@/services/api'
import { deleteDocument, fetchDocuments } from '@/services/documents.service'
import type { KnowledgeDocument } from '@/types/api'

export function DocumentsPage() {
  const toast = useToast()
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [error, setError] = useState('')

  const totals = useMemo(
    () => ({
      documents: documents.length,
      chunks: documents.reduce((sum, document) => sum + document.chunk_count, 0),
      text: documents.reduce((sum, document) => sum + document.text_length, 0),
    }),
    [documents],
  )

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError('')
      try {
        const rows = await fetchDocuments()
        if (!cancelled) setDocuments(rows)
      } catch (err) {
        const message = parseApiError(err)
        if (!cancelled) {
          setError(message)
          toast.error('Could not load documents', message)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [toast])

  const handleUploaded = (document: KnowledgeDocument) => {
    setDocuments((current) => [document, ...current.filter((item) => item.id !== document.id)])
  }

  const handleDelete = async (document: KnowledgeDocument) => {
    const confirmed = window.confirm(`Delete ${document.filename}? This removes it from the AI search index.`)
    if (!confirmed) return

    setDeletingId(document.id)
    try {
      await deleteDocument(document.id)
      setDocuments((current) => current.filter((item) => item.id !== document.id))
      toast.success('Document deleted', `${document.filename} was removed from the RAG index.`)
    } catch (err) {
      toast.error('Delete failed', parseApiError(err))
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <DashboardLayout
      title="AI documents"
      subtitle="Manage the PDFs used by grounded assistant answers"
      navItems={adminNav}
    >
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                <FileText className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Documents</p>
                <p className="text-xl font-semibold">{totals.documents}</p>
              </div>
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                <Database className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Chunks</p>
                <p className="text-xl font-semibold">{totals.chunks.toLocaleString()}</p>
              </div>
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                <Search className="h-4 w-4" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Extracted text</p>
                <p className="text-xl font-semibold">{totals.text.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        <DocumentUpload onUploaded={handleUploaded} />

        {error ? (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        ) : null}

        {loading ? (
          <LoadingState label="Loading documents" />
        ) : (
          <DocumentTable documents={documents} deletingId={deletingId} onDelete={handleDelete} />
        )}
      </div>
    </DashboardLayout>
  )
}
