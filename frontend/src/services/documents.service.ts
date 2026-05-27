import type { KnowledgeDocument } from '@/types/api'
import { api } from './api'

const DOCUMENT_UPLOAD_TIMEOUT_MS = Number(import.meta.env.VITE_DOCUMENT_UPLOAD_TIMEOUT_MS ?? 120000)

export async function fetchDocuments(): Promise<KnowledgeDocument[]> {
  const { data } = await api.get<KnowledgeDocument[]>('/documents')
  return data
}

export async function uploadDocument(
  file: File,
  onProgress?: (progress: number) => void,
): Promise<KnowledgeDocument> {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post<KnowledgeDocument>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: DOCUMENT_UPLOAD_TIMEOUT_MS,
    onUploadProgress: (event) => {
      if (!event.total) return
      onProgress?.(Math.min(95, Math.round((event.loaded / event.total) * 100)))
    },
  })
  onProgress?.(100)
  return data
}

export async function deleteDocument(id: number): Promise<void> {
  await api.delete(`/documents/${id}`)
}
