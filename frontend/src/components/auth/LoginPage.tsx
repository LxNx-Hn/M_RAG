import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { BookOpen, Mail, Lock, User, Loader2 } from 'lucide-react'

interface Props {
  onLogin: (email: string, password: string) => Promise<void>
  onSignup: (email: string, username: string, password: string) => Promise<void>
  onSkip?: () => void
}

export default function LoginPage({ onLogin, onSignup, onSkip }: Props) {
  const { t } = useTranslation()
  const [isSignup, setIsSignup] = useState(false)
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (isSignup) {
        await onSignup(email, username, password)
      } else {
        await onLogin(email, password)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'var(--bg-primary)' }}
    >
      <div
        className="w-full max-w-sm rounded-2xl p-8"
        style={{
          background: 'var(--bg-surface)',
          boxShadow: 'var(--shadow-lg)',
          border: '1px solid var(--border-light)',
        }}
      >
        {/* 로고 */}
        <div className="flex flex-col items-center mb-8">
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center mb-3"
            style={{ background: 'var(--accent-light)' }}
          >
            <BookOpen size={24} style={{ color: 'var(--accent)' }} />
          </div>
          <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
            M-RAG
          </h1>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            {t('common.appDesc')}
          </p>
        </div>

        {/* 탭 */}
        <div
          className="flex rounded-xl p-1 mb-6"
          style={{ background: 'var(--bg-primary)' }}
        >
          <button
            onClick={() => setIsSignup(false)}
            className="flex-1 py-2 rounded-lg text-xs font-medium transition-all"
            style={{
              background: !isSignup ? 'var(--bg-surface)' : 'transparent',
              color: !isSignup ? 'var(--text-primary)' : 'var(--text-muted)',
              boxShadow: !isSignup ? 'var(--shadow-sm)' : 'none',
            }}
          >
            {t('topbar.login')}
          </button>
          <button
            onClick={() => setIsSignup(true)}
            className="flex-1 py-2 rounded-lg text-xs font-medium transition-all"
            style={{
              background: isSignup ? 'var(--bg-surface)' : 'transparent',
              color: isSignup ? 'var(--text-primary)' : 'var(--text-muted)',
              boxShadow: isSignup ? 'var(--shadow-sm)' : 'none',
            }}
          >
            Sign up
          </button>
        </div>

        {/* 폼 */}
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="relative">
            <Mail size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
              className="w-full pl-10 pr-4 py-3 rounded-xl text-[13px] outline-none transition-all"
              style={{
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
              }}
            />
          </div>

          {isSignup && (
            <div className="relative">
              <User size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                required
                className="w-full pl-10 pr-4 py-3 rounded-xl text-[13px] outline-none transition-all"
                style={{
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                }}
              />
            </div>
          )}

          <div className="relative">
            <Lock size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              className="w-full pl-10 pr-4 py-3 rounded-xl text-[13px] outline-none transition-all"
              style={{
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
              }}
            />
          </div>

          {error && (
            <p className="text-xs text-red-500 text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl text-[13px] font-semibold text-white transition-all hover:scale-[0.99] disabled:opacity-50"
            style={{ background: 'var(--accent)' }}
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin mx-auto" />
            ) : isSignup ? (
              'Sign up'
            ) : (
              t('topbar.login')
            )}
          </button>
        </form>

        {/* 스킵 옵션 */}
        {onSkip && (
          <button
            onClick={onSkip}
            className="w-full mt-4 py-2 text-xs transition-colors"
            style={{ color: 'var(--text-muted)' }}
          >
            로그인 없이 사용하기
          </button>
        )}
      </div>
    </div>
  )
}
