import api from './client'
import type { QueryRequest, QueryResponse, SearchRequest, SearchResponse, SSEMetadataEvent, SSEDoneEvent } from '@/types/api'

export async function queryRAG(req: QueryRequest): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>('/api/chat/query', req)
  return data
}

export async function searchRAG(req: SearchRequest): Promise<SearchResponse> {
  const { data } = await api.post<SearchResponse>('/api/chat/search', req)
  return data
}

/** SSE 스트리밍 쿼리 (Phase 2) */
export async function queryRAGStream(
  req: QueryRequest,
  onMetadata: (data: SSEMetadataEvent) => void,
  onToken: (token: string) => void,
  onDone: (data: SSEDoneEvent) => void,
  onError?: (err: Error) => void,
): Promise<void> {
  const token = localStorage.getItem('access_token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  try {
    const response = await fetch('/api/chat/query/stream', {
      method: 'POST',
      headers,
      body: JSON.stringify(req),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      let currentEvent = ''
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6)
          try {
            const data = JSON.parse(jsonStr)
            if (currentEvent === 'metadata') onMetadata(data)
            else if (currentEvent === 'token') onToken(data.token)
            else if (currentEvent === 'done') onDone(data)
          } catch {
            // non-JSON data line
          }
        }
      }
    }
  } catch (err) {
    onError?.(err instanceof Error ? err : new Error(String(err)))
  }
}
