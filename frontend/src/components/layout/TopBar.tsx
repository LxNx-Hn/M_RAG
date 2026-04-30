import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Moon, Sun, LogOut, BookOpen, User, ArrowLeft, UserX } from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import DeleteAccountModal from '@/components/auth/DeleteAccountModal'
import api from '@/api/client'

interface Props {
  onBackToSessions?: () => void
  showBack?: boolean
}

export default function TopBar({ onBackToSessions, showBack }: Props) {
  const { t } = useTranslation()
  const { darkMode, toggleDarkMode } = useUIStore()
  const { user, logout } = useAuthStore()
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const handleLogout = async () => {
    try {
      await api.post('/api/auth/logout')
    } catch {
      // 서버 에러여도 클라이언트는 로그아웃 처리
    }
    logout()
    window.location.replace('/')
  }

  return (
    <>
      <header
        className="h-14 flex items-center justify-between px-4 border-b shrink-0"
        style={{
          background: 'var(--bg-surface)',
          borderColor: 'var(--border-color)',
        }}
      >
        {/* 로고 */}
        <div className="flex items-center gap-2.5">
          {showBack && onBackToSessions && (
            <button
              onClick={onBackToSessions}
              className="flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium transition-all hover:scale-105 mr-1"
              style={{
                background: 'var(--bg-primary)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-color)',
              }}
            >
              <ArrowLeft size={13} />
              <span className="hidden sm:inline">{t('topbar.backToSessions')}</span>
            </button>
          )}
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: 'var(--accent-light)' }}
          >
            <BookOpen size={18} style={{ color: 'var(--accent)' }} />
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>
              {t('common.appName')}
            </h1>
            <p className="text-[10px] leading-tight" style={{ color: 'var(--text-muted)' }}>
              {t('common.appDesc')}
            </p>
          </div>
        </div>

        {/* 컨트롤 */}
        <div className="flex items-center gap-2">
          {/* 사용자 정보 */}
          {user && (
            <div
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs"
              style={{ background: 'var(--bg-primary)', color: 'var(--text-secondary)' }}
            >
              <User size={13} />
              <span className="font-medium max-w-[120px] truncate">{user.username || user.email}</span>
            </div>
          )}

          {/* 다크모드 토글 */}
          <button
            onClick={toggleDarkMode}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:scale-105"
            style={{
              background: darkMode ? 'rgba(250,204,21,0.12)' : 'rgba(99,102,241,0.08)',
              color: darkMode ? '#facc15' : '#6366f1',
            }}
            title={darkMode ? t('topbar.lightMode') : t('topbar.darkMode')}
          >
            {darkMode ? <Sun size={16} /> : <Moon size={16} />}
          </button>

          {/* 회원 탈퇴 */}
          <button
            onClick={() => setShowDeleteModal(true)}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition-all hover:scale-105"
            style={{
              background: 'rgba(239,68,68,0.05)',
              color: '#9ca3af',
            }}
            title={t('topbar.deleteAccount')}
          >
            <UserX size={14} />
          </button>

          {/* 로그아웃 */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all hover:scale-105"
            style={{
              background: 'rgba(239,68,68,0.08)',
              color: '#ef4444',
            }}
            title={t('topbar.logout')}
          >
            <LogOut size={13} />
            <span className="hidden sm:inline">{t('topbar.logout')}</span>
          </button>
        </div>
      </header>

      {showDeleteModal && <DeleteAccountModal onClose={() => setShowDeleteModal(false)} />}
    </>
  )
}
