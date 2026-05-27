import { useState } from 'react'
import { Upload } from 'lucide-react'
import { useToast } from '@/context/ToastContext'
import { parseApiError } from '@/services/api'
import { uploadDocument } from '@/services/documents.service'
import type { KnowledgeDocument } from '@/types/api'
import { UploadDropzone } from './UploadDropzone'

interface DocumentUploadProps {
  onUploaded: (document: KnowledgeDocument) => void
}

export function DocumentUpload({ onUploaded }: DocumentUploadProps) {
  const toast = useToast()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleUpload = async () => {
    if (!selectedFile) return
    setUploading(true)
    setProgress(1)
    try {
      const document = await uploadDocument(selectedFile, setProgress)
      onUploaded(document)
      setSelectedFile(null)
      toast.success('Document indexed', `${document.filename} is available to the AI assistant.`)
    } catch (error) {
      toast.error('Upload failed', parseApiError(error))
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  return (
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold">Upload knowledge PDF</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Uploaded PDFs are chunked, embedded locally, and added to the RAG search index.
          </p>
        </div>
        <button
          type="button"
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <Upload className="h-4 w-4" />
          {uploading ? 'Indexing' : 'Upload'}
        </button>
      </div>
      <div className="mt-4">
        <UploadDropzone
          selectedFile={selectedFile}
          disabled={uploading}
          progress={progress}
          onFileSelect={setSelectedFile}
          onInvalidFile={() => toast.error('Unsupported file', 'Please choose a PDF document.')}
        />
      </div>
    </section>
  )
}
