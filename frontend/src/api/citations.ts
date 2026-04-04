import api from './client'
import type { CitationRequest, CitationResponse } from '@/types/api'

export async function trackCitations(req: CitationRequest): Promise<CitationResponse> {
  const { data } = await api.post<CitationResponse>('/api/citations/track', req)
  return data
}
