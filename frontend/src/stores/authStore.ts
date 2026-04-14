import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  user: { id: string; email: string; username: string } | null
  token: string | null
  login: (token: string, user: { id: string; email: string; username: string }) => void
  logout: () => void
  skipAuth: () => boolean
}

const canSkipAuth = import.meta.env.DEV
const hasDevSkip = canSkipAuth && localStorage.getItem('skip_auth') === 'true'

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('access_token') || hasDevSkip,
  user: null,
  token: localStorage.getItem('access_token'),

  login: (token, user) => {
    localStorage.setItem('access_token', token)
    localStorage.removeItem('skip_auth')
    set({ isAuthenticated: true, token, user })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('skip_auth')
    set({ isAuthenticated: false, token: null, user: null })
  },

  skipAuth: () => {
    if (!canSkipAuth) {
      return false
    }
    localStorage.setItem('skip_auth', 'true')
    set({ isAuthenticated: true })
    return true
  },
}))
