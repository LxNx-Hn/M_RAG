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
  const canSkipAuth = import.meta.env.DEV

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
      if (canSkipAuth && skipAuth()) {
        return
      }
      throw error instanceof Error ? error : new Error('Login failed')
    }
  }

  const handleSignup = async (email: string, username: string, password: string) => {
    try {
      const { data } = await api.post('/api/auth/register', { email, username, password })
      login(data.access_token, data.user)
    } catch (error) {
      if (canSkipAuth && skipAuth()) {
        return
      }
      throw error instanceof Error ? error : new Error('Signup failed')
    }
  }

  if (!isAuthenticated) {
    return (
      <LoginPage
        onLogin={handleLogin}
        onSignup={handleSignup}
        onSkip={canSkipAuth ? () => { skipAuth() } : undefined}
      />
    )
  }

  return <AppLayout />
}
