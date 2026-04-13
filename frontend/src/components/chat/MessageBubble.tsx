import { memo, useState } from 'react'
import { User, Bot, FileText, Copy, Check, Download } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '@/types/chat'
import { useChatStore } from '@/stores/chatStore'
import { usePaperStore } from '@/stores/paperStore'
import { copyToClipboard, formatMessageAsMarkdown, downloadAsMarkdown } from '@/utils/export'
import { exportPPT } from '@/api/chat'
import RouteBadge from './RouteBadge'
import FlashcardViewer from './FlashcardViewer'

interface Props {
  message: Message
  onFollowUpClick?: (query: string) => void
}

export default memo(function MessageBubble({ message, onFollowUpClick }: Props) {
  const setHighlightedSource = useChatStore((s) => s.setHighlightedSource)
  const setActivePaper = usePaperStore((s) => s.setActivePaper)
  const setActivePage = usePaperStore((s) => s.setActivePage)
  const [copied, setCopied] = useState(false)

  const isUser = message.role === 'user'

  const handleCopy = async () => {
    const ok = await copyToClipboard(message.content)
    if (ok) {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    }
  }

  const handleDownload = () => {
    downloadAsMarkdown(formatMessageAsMarkdown(message))
  }

  return (
    <div className={`flex gap-2.5 animate-fade-in ${isUser ? 'justify-end' : ''}`}>
      {/* 아바타 */}
      {!isUser && (
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
          style={{ background: 'var(--accent-light)' }}
        >
          <Bot size={14} style={{ color: 'var(--accent)' }} />
        </div>
      )}

      {/* 메시지 내용 */}
      <div
        className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 ${
          isUser ? 'rounded-br-md' : 'rounded-bl-md'
        }`}
        style={{
          background: isUser ? 'var(--accent)' : 'var(--bg-primary)',
          color: isUser ? 'white' : 'var(--text-primary)',
          border: isUser ? 'none' : '1px solid var(--border-light)',
        }}
      >
        {/* 라우트 배지 */}
        {message.route && <RouteBadge route={message.route} />}

        {/* 본문 */}
        <div className="text-[13px] leading-relaxed prose-sm max-w-none">
          {message.isStreaming && !message.content ? (
            <div className="flex items-center gap-1.5">
              <div className="flex gap-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" style={{ animation: 'pulse-dot 1.2s infinite 0s' }} />
                <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" style={{ animation: 'pulse-dot 1.2s infinite 0.2s' }} />
                <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" style={{ animation: 'pulse-dot 1.2s infinite 0.4s' }} />
              </div>
            </div>
          ) : isUser ? (
            <span>{message.content}</span>
          ) : message.pipeline === 'F_flashcard' ? (
            <>
              <FlashcardViewer content={message.content} />
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          )}
          {message.isStreaming && message.content && (
            <span
              className="inline-block w-0.5 h-4 ml-0.5 align-middle"
              style={{ background: 'var(--accent)', animation: 'pulse-dot 0.8s infinite' }}
            />
          )}
        </div>

        {/* 내보내기 버튼 */}
        {!isUser && !message.isStreaming && message.content && (
          <div className="flex gap-1 mt-1.5">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] transition-colors"
              style={{ color: 'var(--text-muted)' }}
              title="Copy"
            >
              {copied ? <Check size={10} /> : <Copy size={10} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] transition-colors"
              style={{ color: 'var(--text-muted)' }}
              title="Download MD"
            >
              <Download size={10} />
              MD
            </button>
            {message.pipeline?.startsWith('E') && (
              <button
                onClick={() => exportPPT(message.content)}
                className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] transition-colors"
                style={{ color: 'var(--text-muted)' }}
                title="Download PPT"
              >
                <Download size={10} />
                PPT
              </button>
            )}
          </div>
        )}

        {/* 출처 */}
        {message.sources && message.sources.length > 0 && !message.isStreaming && (
          <div className="mt-2 pt-2" style={{ borderTop: '1px solid var(--border-light)' }}>
            <p className="text-[10px] font-medium mb-1" style={{ color: 'var(--text-muted)' }}>
              출처 ({message.sources.length})
            </p>
            <div className="space-y-1">
              {message.sources.slice(0, 5).map((src, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setHighlightedSource(src)
                    if (src.doc_id) setActivePaper(src.doc_id)
                    if (src.page > 0) setActivePage(src.page)
                  }}
                  className="flex items-center gap-1.5 text-[10px] px-2 py-1 rounded-md w-full text-left transition-colors hover:scale-[0.99]"
                  style={{
                    background: 'var(--accent-bg)',
                    color: 'var(--accent)',
                  }}
                >
                  <FileText size={10} />
                  <span className="truncate">
                    [{src.section_type}] p.{src.page} — {src.content.slice(0, 60)}...
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 추천 질문 말풍선 */}
        {message.followUps && message.followUps.length > 0 && !message.isStreaming && (
          <div className="mt-2 pt-2 flex flex-wrap gap-1.5" style={{ borderTop: '1px solid var(--border-light)' }}>
            {message.followUps.map((q, i) => (
              <button
                key={i}
                onClick={() => onFollowUpClick?.(q)}
                className="px-3 py-1.5 rounded-full text-[11px] font-medium transition-all hover:scale-105"
                style={{
                  background: 'var(--accent-light)',
                  color: 'var(--accent)',
                  border: '1px solid var(--accent)',
                  borderColor: 'color-mix(in srgb, var(--accent) 30%, transparent)',
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 유저 아바타 */}
      {isUser && (
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
          style={{ background: 'var(--pastel-purple, #f3e8ff)' }}
        >
          <User size={14} style={{ color: '#8b5cf6' }} />
        </div>
      )}
    </div>
  )
})
