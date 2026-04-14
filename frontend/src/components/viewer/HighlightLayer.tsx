import { useMemo } from 'react'
import type { SourceDocument } from '@/types/api'

interface Props {
  source: SourceDocument | null
  zoom: number
  pageNumber: number
  canvasWidth: number
  canvasHeight: number
}

const highlightFadeKeyframes = `
@keyframes mrag-highlight-fade {
  0% { opacity: 0.95; }
  70% { opacity: 0.9; }
  100% { opacity: 0; }
}
`

export default function HighlightLayer({ source, zoom, pageNumber }: Props) {
  const animationKey = useMemo(() => {
    if (!source) return ''
    return `${source.chunk_id}-${source.page}-${source.score}`
  }, [source])

  if (!source || source.page !== pageNumber) return null

  if (source.bbox && source.bbox.length > 0) {
    return (
      <>
        <style>{highlightFadeKeyframes}</style>
        {source.bbox.map((box, i) => {
          const [x0, y0, x1, y1] = box
          const scale = zoom * 1.5
          return (
            <div
              key={`${animationKey}-${i}`}
              className="absolute"
              style={{
                left: x0 * scale,
                top: y0 * scale,
                width: (x1 - x0) * scale,
                height: (y1 - y0) * scale,
                background: 'rgba(56, 189, 248, 0.2)',
                border: '2px solid rgba(56, 189, 248, 0.5)',
                borderRadius: 4,
                pointerEvents: 'none',
                animation: 'mrag-highlight-fade 5s ease-out forwards',
              }}
            />
          )
        })}
      </>
    )
  }

  return (
    <>
      <style>{highlightFadeKeyframes}</style>
      <div
        key={animationKey}
        className="absolute inset-0 pointer-events-none"
        style={{
          border: '3px solid rgba(56, 189, 248, 0.4)',
          borderRadius: 8,
          background: 'rgba(56, 189, 248, 0.05)',
          animation: 'mrag-highlight-fade 5s ease-out forwards',
        }}
      />
    </>
  )
}
