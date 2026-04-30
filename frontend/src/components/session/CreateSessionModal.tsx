import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { X, Loader2 } from 'lucide-react'
import { useSessionStore, type SessionItem } from '@/stores/sessionStore'

interface Props {
  onClose: () => void
  onCreated: (session: SessionItem) => void
}

export default function CreateSessionModal({ onClose, onCreated }: Props) {
  const { t } = useTranslation()
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const createSession = useSessionStore((s) => s.createSession)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const session = await createSession(title.trim() || t('session.untitled'))
      onCreated(session)
    } catch {
      setError(t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.5)' }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl p-6 shadow-2xl"
        style={{ background: 'var(--bg-surface)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
            {t('session.create')}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg transition-colors hover:scale-110"
            style={{ color: 'var(--text-muted)' }}
          >
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={t('session.untitled')}
            className="w-full px-3 py-2.5 rounded-xl text-sm outline-none mb-4"
            style={{
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
            }}
            autoFocus
          />

          {error && (
            <p className="text-xs text-red-500 mb-3">{error}</p>
          )}

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium transition-all"
              style={{ color: 'var(--text-secondary)' }}
            >
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-xl text-xs font-medium text-white transition-all hover:scale-105 disabled:opacity-50"
              style={{ background: 'var(--accent)' }}
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : t('common.confirm')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
