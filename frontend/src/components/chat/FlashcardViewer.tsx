import { useState } from 'react'
import { ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react'

interface Flashcard {
  front: string
  back: string
}

interface Props {
  content: string
}

function parseFlashcards(content: string): Flashcard[] {
  // [FLASHCARD_START] ... [FLASHCARD_END] 마커 사이의 JSON 추출
  const startMarker = '[FLASHCARD_START]'
  const endMarker = '[FLASHCARD_END]'
  const startIdx = content.indexOf(startMarker)
  const endIdx = content.indexOf(endMarker)

  let jsonStr = ''
  if (startIdx !== -1 && endIdx !== -1) {
    jsonStr = content.slice(startIdx + startMarker.length, endIdx).trim()
  } else {
    // 마커 없으면 전체에서 JSON 배열 추출 시도
    const match = content.match(/\[[\s\S]*\]/)
    if (match) jsonStr = match[0]
  }

  try {
    const cards = JSON.parse(jsonStr)
    if (Array.isArray(cards) && cards.length > 0 && cards[0].front) {
      return cards
    }
  } catch {
    // JSON 파싱 실패
  }
  return []
}

export default function FlashcardViewer({ content }: Props) {
  const cards = parseFlashcards(content)
  const [currentIdx, setCurrentIdx] = useState(0)
  const [flipped, setFlipped] = useState(false)

  if (cards.length === 0) {
    // 파싱 실패 시 마크다운으로 fallback
    return null
  }

  const card = cards[currentIdx]

  return (
    <div className="my-2">
      {/* 카드 */}
      <div
        onClick={() => setFlipped(!flipped)}
        className="relative cursor-pointer rounded-xl p-5 min-h-[140px] flex items-center justify-center text-center transition-all duration-300 select-none"
        style={{
          background: flipped ? 'var(--accent-light)' : 'var(--bg-secondary)',
          border: `1.5px solid ${flipped ? 'var(--accent)' : 'var(--border-color)'}`,
          transform: flipped ? 'rotateY(0deg)' : 'rotateY(0deg)',
        }}
      >
        <div>
          <p
            className="text-[10px] font-medium mb-2"
            style={{ color: 'var(--text-muted)' }}
          >
            {flipped ? 'ANSWER' : 'QUESTION'} — {currentIdx + 1}/{cards.length}
          </p>
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
            {flipped ? card.back : card.front}
          </p>
          <p className="text-[10px] mt-3" style={{ color: 'var(--text-muted)' }}>
            click to flip
          </p>
        </div>
      </div>

      {/* 네비게이션 */}
      <div className="flex items-center justify-center gap-3 mt-2">
        <button
          onClick={() => { setCurrentIdx(Math.max(0, currentIdx - 1)); setFlipped(false) }}
          disabled={currentIdx === 0}
          className="p-1.5 rounded-lg transition-colors disabled:opacity-30"
          style={{ color: 'var(--text-secondary)' }}
        >
          <ChevronLeft size={16} />
        </button>
        <button
          onClick={() => setFlipped(!flipped)}
          className="p-1.5 rounded-lg transition-colors"
          style={{ color: 'var(--accent)' }}
          title="Flip card"
        >
          <RotateCcw size={14} />
        </button>
        <button
          onClick={() => { setCurrentIdx(Math.min(cards.length - 1, currentIdx + 1)); setFlipped(false) }}
          disabled={currentIdx === cards.length - 1}
          className="p-1.5 rounded-lg transition-colors disabled:opacity-30"
          style={{ color: 'var(--text-secondary)' }}
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  )
}
