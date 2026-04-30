import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { X, AlertTriangle, Loader2 } from 'lucide-react'
import api from '@/api/client'
import { useAuthStore } from '@/stores/authStore'

interface Props {
  onClose: () => void
}

export default function DeleteAccountModal({ onClose }: Props) {
  const { t } = useTranslation()
  const [confirmText, setConfirmText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const logout = useAuthStore((s) => s.logout)

  const isConfirmed = confirmText === t('account.deleteConfirmText')

  const handleDelete = async () => {
    if (!isConfirmed) return
    setLoading(true)
    setError('')
    try {
      await api.delete('/api/auth/account', {
        data: { confirm_text: confirmText },
      })
      logout()
      window.location.replace('/')
    } catch {
      setError(t('common.error'))
      setLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.6)' }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm rounded-2xl p-6 shadow-2xl"
        style={{ background: 'var(--bg-surface)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle size={18} style={{ color: '#ef4444' }} />
            <h2 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
              {t('account.deleteTitle')}
            </h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg" style={{ color: 'var(--text-muted)' }}>
            <X size={16} />
          </button>
        </div>

        <p className="text-xs mb-4 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          {t('account.deleteWarning')}
        </p>

        <label className="text-[11px] font-medium block mb-1.5" style={{ color: 'var(--text-muted)' }}>
          {t('account.deleteConfirmLabel')}
        </label>
        <input
          type="text"
          value={confirmText}
          onChange={(e) => setConfirmText(e.target.value)}
          placeholder={t('account.deleteConfirmText')}
          className="w-full px-3 py-2 rounded-xl text-sm outline-none mb-4"
          style={{
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
          }}
        />

        {error && <p className="text-xs text-red-500 mb-3">{error}</p>}

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-medium"
            style={{ color: 'var(--text-secondary)' }}
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleDelete}
            disabled={!isConfirmed || loading}
            className="px-4 py-2 rounded-xl text-xs font-medium text-white transition-all disabled:opacity-30"
            style={{ background: '#ef4444' }}
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : t('account.deleteButton')}
          </button>
        </div>
      </div>
    </div>
  )
}
