import { useState, useEffect } from 'react'
import { BookOpen, Download, Loader2, AlertCircle, CheckCircle2, ExternalLink } from 'lucide-react'
import { usePaperStore } from '@/stores/paperStore'
import { listCitations, downloadCitation } from '@/api/citations'
import type { CitationItem } from '@/types/api'

export default function CitationPanel() {
  const activePaperId = usePaperStore((s) => s.activePaperId)
  const [citations, setCitations] = useState<CitationItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [downloadingIdx, setDownloadingIdx] = useState<number | null>(null)

  useEffect(() => {
    if (!activePaperId) {
      setCitations([])
      return
    }

    const fetchCitations = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await listCitations({ doc_id: activePaperId })
        setCitations(res.citations)
      } catch (err) {
        setError('참고문헌을 불러올 수 없습니다')
        console.error('Citation fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchCitations()
  }, [activePaperId])

  const handleDownload = async (index: number) => {
    if (!activePaperId || downloadingIdx !== null) return
    setDownloadingIdx(index)
    try {
      const res = await downloadCitation({
        doc_id: activePaperId,
        citation_index: index,
      })
      if (res.success && res.citation) {
        setCitations((prev) =>
          prev.map((c, i) =>
            i === index ? { ...c, fetched: true, has_pdf: true, fetch_error: null } : c
          )
        )
      }
    } catch (err) {
      console.error('Citation download error:', err)
    } finally {
      setDownloadingIdx(null)
    }
  }

  if (!activePaperId) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
          논문을 선택하면 참고문헌이 표시됩니다
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <Loader2 size={20} className="animate-spin" style={{ color: 'var(--accent)' }} />
        <span className="ml-2 text-xs" style={{ color: 'var(--text-muted)' }}>
          참고문헌 분석 중...
        </span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <AlertCircle size={16} style={{ color: 'var(--text-muted)' }} />
        <span className="ml-2 text-xs" style={{ color: 'var(--text-muted)' }}>{error}</span>
      </div>
    )
  }

  if (citations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4">
        <BookOpen size={24} style={{ color: 'var(--text-muted)' }} />
        <p className="mt-2 text-xs" style={{ color: 'var(--text-muted)' }}>
          참고문헌이 없습니다
        </p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-3 space-y-2">
      <p className="text-[10px] font-medium mb-2" style={{ color: 'var(--text-muted)' }}>
        참고문헌 ({citations.length})
      </p>
      {citations.map((c, i) => {
        const isUnavailable = !!c.fetch_error
        const isDownloading = downloadingIdx === i

        return (
          <div
            key={c.ref_id}
            className="rounded-lg p-2.5 text-xs transition-all"
            style={{
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-light)',
              opacity: isUnavailable ? 0.6 : 1,
            }}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                  [{c.ref_id}] {c.title}
                </p>
                <p className="text-[10px] mt-0.5 truncate" style={{ color: 'var(--text-muted)' }}>
                  {c.authors}{c.year ? ` (${c.year})` : ''}
                </p>
              </div>

              {/* 상태 아이콘 */}
              <div className="shrink-0 flex items-center gap-1">
                {c.fetched && (
                  <CheckCircle2 size={12} className="text-green-500" />
                )}
                {c.arxiv_id && (
                  <a
                    href={`https://arxiv.org/abs/${c.arxiv_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:scale-110 transition-transform"
                    title="arXiv"
                  >
                    <ExternalLink size={12} style={{ color: 'var(--accent)' }} />
                  </a>
                )}
              </div>
            </div>

            {/* 액션 */}
            <div className="mt-1.5 flex items-center gap-1.5">
              {isUnavailable ? (
                <span
                  className="px-2 py-0.5 rounded text-[9px]"
                  style={{ background: 'var(--border-light)', color: 'var(--text-muted)' }}
                  title={c.fetch_error || ''}
                >
                  arXiv 미등록 — PDF 직접 업로드 필요
                </span>
              ) : c.has_pdf && !c.fetched ? (
                <button
                  onClick={() => handleDownload(i)}
                  disabled={isDownloading}
                  className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-medium transition-all hover:scale-105 disabled:opacity-50"
                  style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}
                >
                  {isDownloading ? (
                    <Loader2 size={10} className="animate-spin" />
                  ) : (
                    <Download size={10} />
                  )}
                  다운로드 & 인덱싱
                </button>
              ) : c.fetched ? (
                <span
                  className="px-2 py-0.5 rounded text-[9px]"
                  style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}
                >
                  인덱싱 완료
                </span>
              ) : null}
            </div>
          </div>
        )
      })}
    </div>
  )
}
