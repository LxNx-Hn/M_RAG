import { useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { Upload, FileText, Trash2, Loader2 } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { usePaperStore } from '@/stores/paperStore'
import { uploadPaper, listPapers, deletePaper } from '@/api/papers'
import { SECTION_COLORS } from '@/types/paper'

export default function SourcePanel() {
  const { t } = useTranslation()
  const { papers, activePaperId, uploading, setPapers, addPaper, removePaper, setActivePaper, setUploading } =
    usePaperStore()

  // 논문 목록 로드
  useEffect(() => {
    listPapers()
      .then((res) => {
        const paperList = res.collections.map((c) => ({
          doc_id: c.name,
          title: c.name.replace(/_/g, ' '),
          total_pages: 0,
          num_chunks: c.count,
          sections: {},
        }))
        setPapers(paperList)
      })
      .catch(() => {})
  }, [setPapers])

  const onDrop = useCallback(
    async (files: File[]) => {
      for (const file of files) {
        setUploading(true)
        try {
          const res = await uploadPaper(file)
          if (res.success && res.paper) {
            addPaper({
              doc_id: res.paper.doc_id,
              title: res.paper.title,
              total_pages: res.paper.total_pages,
              num_chunks: res.paper.num_chunks,
              sections: res.paper.sections,
              filename: file.name,
            })
            if (!activePaperId) setActivePaper(res.paper.doc_id)
          }
        } catch (err) {
          console.error('Upload failed:', err)
        } finally {
          setUploading(false)
        }
      }
    },
    [addPaper, activePaperId, setActivePaper, setUploading]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: true,
  })

  const handleDelete = async (docId: string) => {
    try {
      await deletePaper(docId)
      removePaper(docId)
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 헤더 */}
      <div className="p-4 pb-3">
        <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
          {t('source.title')}
        </h2>
      </div>

      {/* 업로드 영역 */}
      <div className="px-4 pb-3">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
            isDragActive ? 'scale-[0.98]' : 'hover:scale-[0.99]'
          }`}
          style={{
            borderColor: isDragActive ? 'var(--accent)' : 'var(--border-color)',
            background: isDragActive ? 'var(--accent-bg)' : 'transparent',
          }}
        >
          <input {...getInputProps()} />
          {uploading ? (
            <div className="flex flex-col items-center gap-2 py-2">
              <Loader2 size={20} className="animate-spin" style={{ color: 'var(--accent)' }} />
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {t('source.uploading')}
              </span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 py-2">
              <Upload size={20} style={{ color: isDragActive ? 'var(--accent)' : 'var(--text-muted)' }} />
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {t('source.uploadHint')}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 논문 목록 */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <h3 className="text-xs font-medium mb-2" style={{ color: 'var(--text-muted)' }}>
          {t('source.papers')} ({papers.length})
        </h3>

        {papers.length === 0 ? (
          <p className="text-xs text-center py-6" style={{ color: 'var(--text-muted)' }}>
            {t('source.noPapers')}
          </p>
        ) : (
          <div className="space-y-2">
            {papers.map((paper) => (
              <div
                key={paper.doc_id}
                onClick={() => setActivePaper(paper.doc_id)}
                className={`rounded-xl p-3 cursor-pointer transition-all hover:scale-[0.99] group`}
                style={{
                  background: activePaperId === paper.doc_id ? 'var(--accent-light)' : 'var(--bg-primary)',
                  border: `1px solid ${activePaperId === paper.doc_id ? 'var(--accent)' : 'var(--border-light)'}`,
                }}
              >
                <div className="flex items-start gap-2.5">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
                    style={{
                      background: activePaperId === paper.doc_id ? 'var(--accent)' : 'var(--border-color)',
                    }}
                  >
                    <FileText
                      size={14}
                      style={{ color: activePaperId === paper.doc_id ? 'white' : 'var(--text-muted)' }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-xs font-medium truncate"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {paper.title}
                    </p>
                    <p className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
                      {paper.num_chunks} {t('source.chunks')}
                      {paper.total_pages > 0 && ` · ${paper.total_pages} ${t('source.pages')}`}
                    </p>
                    {/* 섹션 태그 */}
                    {Object.keys(paper.sections).length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1.5">
                        {Object.entries(paper.sections).map(([section, count]) => (
                          <span
                            key={section}
                            className={`text-[9px] px-1.5 py-0.5 rounded-md font-medium ${
                              SECTION_COLORS[section] || SECTION_COLORS.other
                            }`}
                          >
                            {section} ({count})
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(paper.doc_id)
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <Trash2 size={12} className="text-red-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
