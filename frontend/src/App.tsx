import { useEffect, useState } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import LoginPage from '@/components/auth/LoginPage'
import SessionHub from '@/components/session/SessionHub'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { useSessionStore, type SessionItem } from '@/stores/sessionStore'
import api from '@/api/client'
import '@/i18n'

export default function App() {
  const darkMode = useUIStore((s) => s.darkMode)
  const { isAuthenticated, login } = useAuthStore()
  const { setActiveSession } = useSessionStore()
  const [view, setView] = useState<'hub' | 'workspace'>('hub')

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const handleLogin = async (email: string, password: string) => {
    try {
      const { data } = await api.post('/api/auth/login', { email, password })
      login(data.access_token, data.user)
    } catch (error) {
      throw error instanceof Error ? error : new Error('Login failed')
    }
  }

  const handleSignup = async (email: string, username: string, password: string) => {
    try {
      const { data } = await api.post('/api/auth/register', { email, username, password })
      login(data.access_token, data.user)
    } catch (error) {
      throw error instanceof Error ? error : new Error('Signup failed')
    }
  }

  const handleSelectSession = (session: SessionItem) => {
    setActiveSession(session.id)
    setView('workspace')
  }

  const handleBackToSessions = () => {
    setView('hub')
  }

  if (!isAuthenticated) {
    return (
      <LoginPage
        onLogin={handleLogin}
        onSignup={handleSignup}
      />
    )
  }

  if (view === 'hub') {
    return <SessionHub onSelectSession={handleSelectSession} />
  }

  return <AppLayout onBackToSessions={handleBackToSessions} />
}
