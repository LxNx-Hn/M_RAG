import api from './client'
import type { CitationRequest, CitationResponse, CitationItem } from '@/types/api'

export interface CitationListRequest {
  doc_id: string
  collection_name?: string
}

export interface CitationDownloadRequest {
  doc_id: string
  citation_index: number
  collection_name?: string
}

export interface CitationDownloadResponse {
  success: boolean
  citation: CitationItem | null
  indexed: boolean
  message: string
}

export async function trackCitations(req: CitationRequest): Promise<CitationResponse> {
  const { data } = await api.post<CitationResponse>('/api/citations/track', req)
  return data
}

export async function listCitations(req: CitationListRequest): Promise<CitationResponse> {
  const { data } = await api.post<CitationResponse>('/api/citations/list', req)
  return data
}

export async function downloadCitation(req: CitationDownloadRequest): Promise<CitationDownloadResponse> {
  const { data } = await api.post<CitationDownloadResponse>('/api/citations/download', req)
  return data
}
