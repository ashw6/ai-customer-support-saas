import { useRef, useState, type DragEvent } from 'react'
import { FileUp, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface UploadDropzoneProps {
  disabled?: boolean
  progress?: number
  selectedFile?: File | null
  onFileSelect: (file: File) => void
  onInvalidFile?: () => void
}

function isPdf(file: File) {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
}

export function UploadDropzone({
  disabled = false,
  progress = 0,
  selectedFile,
  onFileSelect,
  onInvalidFile,
}: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [dragging, setDragging] = useState(false)
  const uploading = disabled && progress > 0

  const handleFiles = (files: FileList | null) => {
    const file = files?.[0]
    if (!file) return
    if (!isPdf(file)) {
      onInvalidFile?.()
      return
    }
    onFileSelect(file)
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragging(false)
    if (disabled) return
    handleFiles(event.dataTransfer.files)
  }

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault()
        if (!disabled) setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={cn(
        'rounded-lg border border-dashed border-border bg-background p-6 transition-colors',
        dragging ? 'border-primary bg-primary/5' : 'hover:border-primary/60',
        disabled ? 'cursor-not-allowed opacity-80' : 'cursor-pointer',
      )}
      role="button"
      tabIndex={disabled ? -1 : 0}
      onClick={() => {
        if (!disabled) inputRef.current?.click()
      }}
      onKeyDown={(event) => {
        if (!disabled && (event.key === 'Enter' || event.key === ' ')) inputRef.current?.click()
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        className="sr-only"
        disabled={disabled}
        onChange={(event) => {
          handleFiles(event.target.files)
          event.target.value = ''
        }}
      />
      <div className="flex flex-col items-center text-center">
        <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          {uploading ? <Loader2 className="h-5 w-5 animate-spin" /> : <FileUp className="h-5 w-5" />}
        </div>
        <p className="mt-3 text-sm font-semibold text-foreground">
          {selectedFile ? selectedFile.name : 'Drop a PDF here or choose a file'}
        </p>
        <p className="mt-1 text-sm text-muted-foreground">PDF only, up to the backend upload limit.</p>
        {uploading ? (
          <div className="mt-4 w-full max-w-sm">
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{progress}% uploaded</p>
          </div>
        ) : null}
      </div>
    </div>
  )
}
