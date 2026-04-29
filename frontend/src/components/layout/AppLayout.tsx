import { lazy, Suspense, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { FileText, MessageCircle, PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen } from 'lucide-react'
import TopBar from './TopBar'
import { useUIStore } from '@/stores/uiStore'

const SourcePanel = lazy(() => import('@/components/source/SourcePanel'))
const PDFViewer = lazy(() => import('@/components/viewer/PDFViewer'))
const ChatPanel = lazy(() => import('@/components/chat/ChatPanel'))

export default function AppLayout() {
  const { t } = useTranslation()
  const { leftPanelOpen, rightPanelOpen, toggleLeftPanel, toggleRightPanel } = useUIStore()
  const [mobileTab, setMobileTab] = useState<'source' | 'viewer' | 'chat'>('viewer')

  return (
    <div className="h-screen flex flex-col" style={{ background: 'var(--bg-primary)' }}>
      <TopBar />

      {/* 데스크탑: 패널 토글 바 */}
      <div
        className="hidden md:flex items-center justify-between px-2 py-1 border-b"
        style={{ background: 'var(--bg-surface)', borderColor: 'var(--border-light)' }}
      >
        {/* 좌측 토글 */}
        <button
          onClick={toggleLeftPanel}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-medium transition-all hover:scale-[1.02]"
          style={{
            background: leftPanelOpen ? 'var(--accent-light)' : 'var(--bg-primary)',
            color: leftPanelOpen ? 'var(--accent)' : 'var(--text-muted)',
            border: `1px solid ${leftPanelOpen ? 'var(--accent)' : 'var(--border-color)'}`,
          }}
        >
          {leftPanelOpen ? <PanelLeftClose size={13} /> : <PanelLeftOpen size={13} />}
          <span>{t('source.title')}</span>
        </button>

        {/* 우측 토글 */}
        <button
          onClick={toggleRightPanel}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-medium transition-all hover:scale-[1.02]"
          style={{
            background: rightPanelOpen ? 'var(--accent-light)' : 'var(--bg-primary)',
            color: rightPanelOpen ? 'var(--accent)' : 'var(--text-muted)',
            border: `1px solid ${rightPanelOpen ? 'var(--accent)' : 'var(--border-color)'}`,
          }}
        >
          <span>{t('chat.title')}</span>
          {rightPanelOpen ? <PanelRightClose size={13} /> : <PanelRightOpen size={13} />}
        </button>
      </div>

      {/* 모바일 탭 바 */}
      <div
        className="md:hidden flex border-b"
        style={{ background: 'var(--bg-surface)', borderColor: 'var(--border-color)' }}
      >
        {(['source', 'viewer', 'chat'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setMobileTab(tab)}
            className="flex-1 py-2.5 text-[11px] font-medium transition-colors relative"
            style={{
              color: mobileTab === tab ? 'var(--accent)' : 'var(--text-muted)',
            }}
          >
            <div className="flex items-center justify-center gap-1.5">
              {tab === 'source' && <FileText size={13} />}
              {tab === 'viewer' && <BookOpenIcon />}
              {tab === 'chat' && <MessageCircle size={13} />}
              <span>
                {tab === 'source' ? t('source.title') : tab === 'viewer' ? t('viewer.title') : t('chat.title')}
              </span>
            </div>
            {mobileTab === tab && (
              <div
                className="absolute bottom-0 left-1/4 right-1/4 h-[2px] rounded-full"
                style={{ background: 'var(--accent)' }}
              />
            )}
          </button>
        ))}
      </div>

      {/* 메인 3패널 (데스크탑만) */}
      <div className="hidden md:flex flex-1 overflow-hidden">
        {/* 좌측 패널 */}
        <div
          className={`hidden md:flex flex-col border-r transition-all duration-300 overflow-hidden ${
            leftPanelOpen ? 'w-72' : 'w-0 border-r-0'
          }`}
          style={{ background: 'var(--bg-surface)', borderColor: 'var(--border-color)' }}
        >
          {leftPanelOpen && (
            <Suspense fallback={<PanelFallback label={t('source.title')} />}>
              <SourcePanel />
            </Suspense>
          )}
        </div>

        {/* 중앙 패널 */}
        <div className="flex-1 flex flex-col min-w-0">
          <Suspense fallback={<PanelFallback label={t('viewer.title')} />}>
            <PDFViewer />
          </Suspense>
        </div>

        {/* 우측 패널 */}
        <div
          className={`hidden md:flex flex-col border-l transition-all duration-300 overflow-hidden ${
            rightPanelOpen ? 'w-96' : 'w-0 border-l-0'
          }`}
          style={{ background: 'var(--bg-surface)', borderColor: 'var(--border-color)' }}
        >
          {rightPanelOpen && (
            <Suspense fallback={<PanelFallback label={t('chat.title')} />}>
              <ChatPanel />
            </Suspense>
          )}
        </div>
      </div>

      {/* 모바일 콘텐츠 */}
      <div className="flex-1 md:hidden overflow-hidden">
        {mobileTab === 'source' && (
          <Suspense fallback={<PanelFallback label={t('source.title')} />}>
            <SourcePanel />
          </Suspense>
        )}
        {mobileTab === 'viewer' && (
          <Suspense fallback={<PanelFallback label={t('viewer.title')} />}>
            <PDFViewer />
          </Suspense>
        )}
        {mobileTab === 'chat' && (
          <Suspense fallback={<PanelFallback label={t('chat.title')} />}>
            <ChatPanel />
          </Suspense>
        )}
      </div>
    </div>
  )
}

function PanelFallback({ label }: { label: string }) {
  return (
    <div className="flex h-full items-center justify-center" style={{ background: 'var(--bg-primary)' }}>
      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
        {label}
      </p>
    </div>
  )
}

function BookOpenIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
    </svg>
  )
}
