import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Trash2, Loader2, BookOpen } from 'lucide-react'
import { useSessionStore, type SessionItem } from '@/stores/sessionStore'
import CreateSessionModal from './CreateSessionModal'

interface Props {
  onSelectSession: (session: SessionItem) => void
}

export default function SessionHub({ onSelectSession }: Props) {
  const { t } = useTranslation()
  const { sessions, loading, fetchSessions, deleteSession } = useSessionStore()
  const [showCreate, setShowCreate] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (!confirm(t('session.deleteConfirm'))) return
    setDeletingId(id)
    try {
      await deleteSession(id)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <div className="max-w-5xl mx-auto px-6 pt-12 pb-8">
        <div className="flex items-center gap-3 mb-2">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: 'var(--accent-light)' }}
          >
            <BookOpen size={20} style={{ color: 'var(--accent)' }} />
          </div>
          <div>
            <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
              {t('common.appName')}
            </h1>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              {t('common.appDesc')}
            </p>
          </div>
        </div>
      </div>

      {/* Session grid */}
      <div className="max-w-5xl mx-auto px-6 pb-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Create new session card */}
          <button
            onClick={() => setShowCreate(true)}
            className="group flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed transition-all hover:scale-[0.98] active:scale-95"
            style={{
              borderColor: 'var(--border-color)',
              background: 'var(--bg-surface)',
              minHeight: '160px',
            }}
          >
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center mb-3 transition-transform group-hover:scale-110"
              style={{ background: 'var(--accent-light)' }}
            >
              <Plus size={20} style={{ color: 'var(--accent)' }} />
            </div>
            <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
              {t('session.create')}
            </span>
          </button>

          {/* Loading */}
          {loading && sessions.length === 0 && (
            <div className="flex items-center justify-center p-8">
              <Loader2 size={20} className="animate-spin" style={{ color: 'var(--text-muted)' }} />
            </div>
          )}

          {/* Session cards */}
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => onSelectSession(session)}
              className="group relative flex flex-col p-5 rounded-2xl border cursor-pointer transition-all hover:scale-[0.98] active:scale-95"
              style={{
                background: 'var(--bg-surface)',
                borderColor: 'var(--border-color)',
                minHeight: '160px',
              }}
            >
              {/* Icon */}
              <span className="text-3xl mb-3">{session.icon}</span>

              {/* Title */}
              <h3
                className="text-sm font-semibold mb-1 line-clamp-2"
                style={{ color: 'var(--text-primary)' }}
              >
                {session.title}
              </h3>

              {/* Meta */}
              <div className="mt-auto flex items-center justify-between">
                <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                  {t('session.paperCount', { count: session.paper_count })}
                </span>
                <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                  {session.updated_at
                    ? new Date(session.updated_at).toLocaleDateString('ko-KR')
                    : ''}
                </span>
              </div>

              {/* Delete button */}
              <button
                onClick={(e) => handleDelete(e, session.id)}
                className="absolute top-3 right-3 p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-all hover:scale-110"
                style={{ background: 'rgba(239,68,68,0.08)', color: '#ef4444' }}
                disabled={deletingId === session.id}
              >
                {deletingId === session.id ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <Trash2 size={12} />
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {showCreate && (
        <CreateSessionModal
          onClose={() => setShowCreate(false)}
          onCreated={(session) => {
            setShowCreate(false)
            onSelectSession(session)
          }}
        />
      )}
    </div>
  )
}
