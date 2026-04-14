import api from './client'
import type {
  QueryRequest,
  QueryResponse,
  SearchRequest,
  SearchResponse,
  SSEErrorEvent,
  SSEMetadataEvent,
  SSEDoneEvent,
} from '@/types/api'

export async function queryRAG(req: QueryRequest): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>('/api/chat/query', req)
  return data
}

export async function searchRAG(req: SearchRequest): Promise<SearchResponse> {
  const { data } = await api.post<SearchResponse>('/api/chat/search', req)
  return data
}

export async function exportPPT(answer: string, title?: string): Promise<void> {
  const response = await api.post('/api/chat/export/ppt', {
    answer,
    title: title || 'M-RAG Summary',
  }, { responseType: 'blob' })
  const url = URL.createObjectURL(response.data)
  const a = document.createElement('a')
  a.href = url
  a.download = 'm-rag-summary.pptx'
  a.click()
  URL.revokeObjectURL(url)
}

async function streamOnce(
  req: QueryRequest,
  onMetadata: (data: SSEMetadataEvent) => void,
  onToken: (token: string) => void,
  onDone: (data: SSEDoneEvent) => void,
  timeoutMs: number,
): Promise<void> {
  const token = localStorage.getItem('access_token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch('/api/chat/query/stream', {
      method: 'POST',
      headers,
      body: JSON.stringify(req),
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
          continue
        }
        if (!line.startsWith('data: ')) {
          continue
        }

        const jsonStr = line.slice(6)
        const data = JSON.parse(jsonStr)
        if (currentEvent === 'metadata') {
          onMetadata(data)
        } else if (currentEvent === 'token') {
          onToken(data.token)
        } else if (currentEvent === 'done') {
          onDone(data)
          return
        } else if (currentEvent === 'error') {
          const err = data as SSEErrorEvent
          throw new Error(err.detail || err.error || 'Streaming failed')
        }
      }
    }

    throw new Error('Stream ended without done event')
  } finally {
    window.clearTimeout(timeoutId)
  }
}

export async function queryRAGStream(
  req: QueryRequest,
  onMetadata: (data: SSEMetadataEvent) => void,
  onToken: (token: string) => void,
  onDone: (data: SSEDoneEvent) => void,
  onError?: (err: Error) => void,
): Promise<void> {
  const maxAttempts = 2
  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      await streamOnce(req, onMetadata, onToken, onDone, 120000)
      return
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err))
      if (attempt === maxAttempts) {
        break
      }
    }
  }

  onError?.(lastError ?? new Error('Streaming failed'))
}
