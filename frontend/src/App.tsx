import { useEffect } from 'react'
import AppLayout from '@/components/layout/AppLayout'
import LoginPage from '@/components/auth/LoginPage'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import api from '@/api/client'
import '@/i18n'

export default function App() {
  const darkMode = useUIStore((s) => s.darkMode)
  const { isAuthenticated, login, skipAuth } = useAuthStore()

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
    } catch {
      // Auth 엔드포인트가 아직 없으면 스킵
      skipAuth()
    }
  }

  const handleSignup = async (email: string, username: string, password: string) => {
    try {
      const { data } = await api.post('/api/auth/register', { email, username, password })
      login(data.access_token, data.user)
    } catch {
      skipAuth()
    }
  }

  if (!isAuthenticated) {
    return (
      <LoginPage
        onLogin={handleLogin}
        onSignup={handleSignup}
        onSkip={skipAuth}
      />
    )
  }

  return <AppLayout />
}
