import { create } from 'zustand'
import type { Message, Conversation } from '@/types/chat'
import type { RouteInfo, SourceDocument } from '@/types/api'

interface ChatState {
  conversations: Conversation[]
  activeConversationId: string | null
  isStreaming: boolean
  highlightedSource: SourceDocument | null

  // Actions
  createConversation: () => string
  setActiveConversation: (id: string | null) => void
  addUserMessage: (content: string) => void
  startAssistantMessage: () => void
  appendToken: (token: string) => void
  finalizeAssistantMessage: (
    fullAnswer: string,
    route?: RouteInfo,
    sources?: SourceDocument[],
    steps?: Record<string, unknown>[],
    pipeline?: string,
    followUps?: string[],
  ) => void
  setStreaming: (v: boolean) => void
  setHighlightedSource: (source: SourceDocument | null) => void
  getActiveMessages: () => Message[]
}

let msgCounter = 0
const genId = () => `msg_${Date.now()}_${++msgCounter}`

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  isStreaming: false,
  highlightedSource: null,

  createConversation: () => {
    const id = `conv_${Date.now()}`
    const conv: Conversation = {
      id,
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    set((s) => ({
      conversations: [conv, ...s.conversations],
      activeConversationId: id,
    }))
    return id
  },

  setActiveConversation: (id) => set({ activeConversationId: id }),

  addUserMessage: (content) => {
    const state = get()
    let convId = state.activeConversationId
    if (!convId) {
      convId = state.createConversation()
    }
    const msg: Message = {
      id: genId(),
      role: 'user',
      content,
      createdAt: new Date(),
    }
    set((s) => ({
      conversations: s.conversations.map((c) => {
        if (c.id !== convId) return c
        const title = c.messages.length === 0 ? content.slice(0, 30) : c.title
        return { ...c, title, messages: [...c.messages, msg], updatedAt: new Date() }
      }),
    }))
  },

  startAssistantMessage: () => {
    const convId = get().activeConversationId
    if (!convId) return
    const msg: Message = {
      id: genId(),
      role: 'assistant',
      content: '',
      isStreaming: true,
      createdAt: new Date(),
    }
    set((s) => ({
      isStreaming: true,
      conversations: s.conversations.map((c) =>
        c.id === convId ? { ...c, messages: [...c.messages, msg], updatedAt: new Date() } : c
      ),
    }))
  },

  appendToken: (token) => {
    const convId = get().activeConversationId
    if (!convId) return
    set((s) => ({
      conversations: s.conversations.map((c) => {
        if (c.id !== convId) return c
        const msgs = [...c.messages]
        const last = msgs[msgs.length - 1]
        if (last?.role === 'assistant' && last.isStreaming) {
          msgs[msgs.length - 1] = { ...last, content: last.content + token }
        }
        return { ...c, messages: msgs }
      }),
    }))
  },

  finalizeAssistantMessage: (fullAnswer, route, sources, steps, pipeline, followUps) => {
    const convId = get().activeConversationId
    if (!convId) return
    set((s) => ({
      isStreaming: false,
      conversations: s.conversations.map((c) => {
        if (c.id !== convId) return c
        const msgs = [...c.messages]
        const last = msgs[msgs.length - 1]
        if (last?.role === 'assistant') {
          msgs[msgs.length - 1] = {
            ...last,
            content: fullAnswer,
            route,
            sources,
            steps,
            pipeline,
            followUps,
            isStreaming: false,
          }
        }
        return { ...c, messages: msgs, updatedAt: new Date() }
      }),
    }))
  },

  setStreaming: (isStreaming) => set({ isStreaming }),

  setHighlightedSource: (source) => set({ highlightedSource: source }),

  getActiveMessages: () => {
    const state = get()
    const conv = state.conversations.find((c) => c.id === state.activeConversationId)
    return conv?.messages || []
  },
}))
