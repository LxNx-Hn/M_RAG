import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { ZoomIn, ZoomOut, ChevronLeft, ChevronRight, Maximize2, FileText, BookOpen } from 'lucide-react'
import { usePaperStore } from '@/stores/paperStore'
import { useChatStore } from '@/stores/chatStore'
import HighlightLayer from './HighlightLayer'
import CitationPanel from './CitationPanel'

type ViewerTab = 'pdf' | 'citations'

export default function PDFViewer() {
  const { t } = useTranslation()
  const { activePaperId, activePage, zoom, setActivePage, setZoom } = usePaperStore()
  const highlightedSource = useChatStore((s) => s.highlightedSource)
  const containerRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [totalPages, setTotalPages] = useState(0)
  const [pdfDoc, setPdfDoc] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<ViewerTab>('pdf')

  // PDF 로드
  useEffect(() => {
    if (!activePaperId) {
      setPdfDoc(null)
      setTotalPages(0)
      return
    }

    setLoading(true)
    setError(null)

    const loadPdf = async () => {
      try {
        const pdfjsLib = await import('pdfjs-dist')
        pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`

        const url = `/static/data/${activePaperId}.pdf`
        const doc = await pdfjsLib.getDocument(url).promise
        setPdfDoc(doc)
        setTotalPages(doc.numPages)
        setActivePage(1)
      } catch (err) {
        console.error('PDF load error:', err)
        setError('PDF를 불러올 수 없습니다')
      } finally {
        setLoading(false)
      }
    }

    loadPdf()
  }, [activePaperId, setActivePage])

  // 페이지 렌더링
  useEffect(() => {
    if (!pdfDoc || !canvasRef.current) return

    const renderPage = async () => {
      const page = await pdfDoc.getPage(activePage)
      const viewport = page.getViewport({ scale: zoom * 1.5 })
      const canvas = canvasRef.current!
      const ctx = canvas.getContext('2d')!

      canvas.width = viewport.width
      canvas.height = viewport.height

      await page.render({ canvasContext: ctx, viewport }).promise
    }

    renderPage()
  }, [pdfDoc, activePage, zoom])

  // 하이라이트 소스가 변경되면 해당 페이지로 이동
  useEffect(() => {
    if (highlightedSource && highlightedSource.page > 0) {
      setActivePage(highlightedSource.page)
    }
  }, [highlightedSource, setActivePage])

  if (!activePaperId) {
    return (
      <div className="flex-1 h-full flex items-center justify-center" style={{ background: 'var(--bg-primary)' }}>
        <div className="text-center">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
            style={{ background: 'var(--accent-light)' }}
          >
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ color: 'var(--accent)' }}
            >
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
          </div>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            {t('viewer.noPaper')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      {/* 뷰어 툴바 */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b shrink-0"
        style={{ background: 'var(--bg-surface)', borderColor: 'var(--border-color)' }}
      >
        {/* 탭 토글 */}
        <div className="flex items-center gap-1 mr-3">
          <button
            onClick={() => setActiveTab('pdf')}
            className="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium transition-all"
            style={{
              background: activeTab === 'pdf' ? 'var(--accent-light)' : 'transparent',
              color: activeTab === 'pdf' ? 'var(--accent)' : 'var(--text-muted)',
            }}
          >
            <FileText size={12} />
            PDF
          </button>
          <button
            onClick={() => setActiveTab('citations')}
            className="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-medium transition-all"
            style={{
              background: activeTab === 'citations' ? 'var(--accent-light)' : 'transparent',
              color: activeTab === 'citations' ? 'var(--accent)' : 'var(--text-muted)',
            }}
          >
            <BookOpen size={12} />
            참고문헌
          </button>
        </div>

        {/* 페이지 네비게이션 */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setActivePage(Math.max(1, activePage - 1))}
            disabled={activePage <= 1}
            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors disabled:opacity-30"
            style={{ background: 'var(--bg-primary)' }}
          >
            <ChevronLeft size={14} style={{ color: 'var(--text-secondary)' }} />
          </button>
          <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
            <input
              type="number"
              value={activePage}
              onChange={(e) => {
                const v = parseInt(e.target.value)
                if (v >= 1 && v <= totalPages) setActivePage(v)
              }}
              className="w-8 text-center rounded-md py-0.5 text-xs outline-none"
              style={{
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
              }}
              min={1}
              max={totalPages}
            />
            <span>{t('viewer.of')}</span>
            <span>{totalPages}</span>
          </div>
          <button
            onClick={() => setActivePage(Math.min(totalPages, activePage + 1))}
            disabled={activePage >= totalPages}
            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors disabled:opacity-30"
            style={{ background: 'var(--bg-primary)' }}
          >
            <ChevronRight size={14} style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>

        {/* 줌 컨트롤 */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setZoom(zoom - 0.2)}
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: 'var(--bg-primary)' }}
            title={t('viewer.zoomOut')}
          >
            <ZoomOut size={14} style={{ color: 'var(--text-secondary)' }} />
          </button>
          <span className="text-[10px] w-10 text-center" style={{ color: 'var(--text-muted)' }}>
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => setZoom(zoom + 0.2)}
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: 'var(--bg-primary)' }}
            title={t('viewer.zoomIn')}
          >
            <ZoomIn size={14} style={{ color: 'var(--text-secondary)' }} />
          </button>
          <button
            onClick={() => setZoom(1.0)}
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: 'var(--bg-primary)' }}
            title={t('viewer.fitWidth')}
          >
            <Maximize2 size={14} style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>
      </div>

      {/* PDF 캔버스 (탭 전환 시 display:none으로 상태 보존) */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4 flex justify-center"
        style={{ display: activeTab === 'pdf' ? undefined : 'none' }}
      >
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin w-8 h-8 border-2 border-t-transparent rounded-full" style={{ borderColor: 'var(--accent)', borderTopColor: 'transparent' }} />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{error}</p>
          </div>
        ) : (
          <div className="relative">
            <canvas
              ref={canvasRef}
              className="rounded-lg"
              style={{ boxShadow: 'var(--shadow-md)', maxWidth: '100%', height: 'auto' }}
            />
            <HighlightLayer
              source={highlightedSource}
              zoom={zoom}
              pageNumber={activePage}
              canvasWidth={canvasRef.current?.width || 0}
              canvasHeight={canvasRef.current?.height || 0}
            />
          </div>
        )}
      </div>

      {/* 참고문헌 패널 */}
      {activeTab === 'citations' && (
        <div className="flex-1 overflow-hidden">
          <CitationPanel />
        </div>
      )}
    </div>
  )
}
