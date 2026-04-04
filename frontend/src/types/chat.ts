import type { RouteInfo, SourceDocument } from './api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  route?: RouteInfo
  sources?: SourceDocument[]
  steps?: Record<string, unknown>[]
  pipeline?: string
  isStreaming?: boolean
  createdAt: Date
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}
