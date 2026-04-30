import { create } from 'zustand'
import api from '@/api/client'

export interface SessionItem {
  id: string
  title: string
  icon: string
  collection_name: string
  paper_count: number
  created_at: string | null
  updated_at: string | null
}

interface SessionState {
  sessions: SessionItem[]
  activeSessionId: string | null
  loading: boolean

  fetchSessions: () => Promise<void>
  createSession: (title: string) => Promise<SessionItem>
  deleteSession: (id: string) => Promise<void>
  setActiveSession: (id: string | null) => void
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  activeSessionId: null,
  loading: false,

  fetchSessions: async () => {
    set({ loading: true })
    try {
      const { data } = await api.get('/api/sessions')
      set({ sessions: data.sessions || [], loading: false })
    } catch {
      set({ loading: false })
    }
  },

  createSession: async (title: string) => {
    const { data } = await api.post('/api/sessions', { title })
    set((s) => ({ sessions: [data, ...s.sessions] }))
    return data
  },

  deleteSession: async (id: string) => {
    await api.delete(`/api/sessions/${id}`)
    set((s) => ({
      sessions: s.sessions.filter((sess) => sess.id !== id),
      activeSessionId: s.activeSessionId === id ? null : s.activeSessionId,
    }))
  },

  setActiveSession: (id) => set({ activeSessionId: id }),
}))
