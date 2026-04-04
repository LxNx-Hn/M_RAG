import { useEffect, useState } from 'react'
import type { SourceDocument } from '@/types/api'

interface Props {
  source: SourceDocument | null
  zoom: number
  pageNumber: number
  canvasWidth: number
  canvasHeight: number
}

export default function HighlightLayer({ source, zoom, pageNumber }: Props) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (source && source.page === pageNumber) {
      setVisible(true)
      const timer = setTimeout(() => setVisible(false), 5000)
      return () => clearTimeout(timer)
    }
    setVisible(false)
  }, [source, pageNumber])

  if (!visible || !source || source.page !== pageNumber) return null

  // bbox가 있으면 정확한 위치, 없으면 페이지 중앙 일부 하이라이트
  if (source.bbox && source.bbox.length > 0) {
    return (
      <>
        {source.bbox.map((box, i) => {
          const [x0, y0, x1, y1] = box
          const scale = zoom * 1.5 // match PDFViewer render scale
          return (
            <div
              key={i}
              className="absolute transition-opacity duration-500"
              style={{
                left: x0 * scale,
                top: y0 * scale,
                width: (x1 - x0) * scale,
                height: (y1 - y0) * scale,
                background: 'rgba(56, 189, 248, 0.2)',
                border: '2px solid rgba(56, 189, 248, 0.5)',
                borderRadius: 4,
                pointerEvents: 'none',
                animation: 'fadeIn 0.3s ease-out',
              }}
            />
          )
        })}
      </>
    )
  }

  // bbox 없으면 페이지 전체에 부드러운 테두리 표시
  return (
    <div
      className="absolute inset-0 pointer-events-none transition-opacity duration-500"
      style={{
        border: '3px solid rgba(56, 189, 248, 0.4)',
        borderRadius: 8,
        background: 'rgba(56, 189, 248, 0.05)',
      }}
    />
  )
}
