import api from './client'
import type { UploadResponse, CollectionListResponse, PaperInfo } from '@/types/api'

export async function uploadPaper(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<UploadResponse>('/api/papers/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  })
  return data
}

export async function listPapers(): Promise<CollectionListResponse> {
  const { data } = await api.get<CollectionListResponse>('/api/papers/list')
  return data
}

export async function getPaper(docId: string): Promise<PaperInfo> {
  const { data } = await api.get<PaperInfo>(`/api/papers/${docId}`)
  return data
}

export async function deletePaper(name: string): Promise<void> {
  await api.delete(`/api/papers/${name}`)
}
