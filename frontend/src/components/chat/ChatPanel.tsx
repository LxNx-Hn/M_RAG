import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Send, Plus, Loader2, Sparkles, Download } from 'lucide-react'
import { useChatStore } from '@/stores/chatStore'
import { usePaperStore } from '@/stores/paperStore'
import { queryRAG, queryRAGStream } from '@/api/chat'
import { formatConversationAsMarkdown, downloadAsMarkdown } from '@/utils/export'
import MessageBubble from './MessageBubble'

export default function ChatPanel() {
  const { t } = useTranslation()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const {
    isStreaming,
    createConversation,
    addUserMessage,
    startAssistantMessage,
    appendToken,
    finalizeAssistantMessage,
    getActiveMessages,
  } = useChatStore()

  const papers = usePaperStore((s) => s.papers)
  const messages = getActiveMessages()

  // 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const suggestions = [
    t('chat.suggestions.q1'),
    t('chat.suggestions.q2'),
    t('chat.suggestions.q3'),
    t('chat.suggestions.q4'),
    t('chat.suggestions.q5'),
  ]

  const handleSend = async (query?: string) => {
    const text = query || input.trim()
    if (!text || isStreaming) return

    setInput('')
    addUserMessage(text)
    startAssistantMessage()

    let streamRoute: import('@/types/api').RouteInfo | undefined
    let streamSources: import('@/types/api').SourceDocument[] | undefined

    try {
      await queryRAGStream(
        { query: text },
        (metadata) => {
          streamRoute = metadata.route
          streamSources = metadata.sources
        },
        (token) => {
          appendToken(token)
        },
        (doneData) => {
          finalizeAssistantMessage(
            doneData.full_answer,
            streamRoute,
            streamSources,
            undefined,
            undefined,
            doneData.follow_ups,
          )
        },
        async () => {
          // SSE 실패 시 일반 쿼리 폴백
          try {
            const res = await queryRAG({ query: text })
            finalizeAssistantMessage(
              res.answer,
              res.route,
              res.sources,
              res.steps,
              res.pipeline,
              res.follow_ups,
            )
          } catch {
            finalizeAssistantMessage('오류가 발생했습니다. 다시 시도해주세요.')
          }
        }
      )
    } catch {
      try {
        const res = await queryRAG({ query: text })
        finalizeAssistantMessage(
          res.answer,
          res.route,
          res.sources,
          res.steps,
          res.pipeline,
          res.follow_ups,
        )
      } catch {
        finalizeAssistantMessage('오류가 발생했습니다. 다시 시도해주세요.')
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 헤더 */}
      <div
        className="flex items-center justify-between p-4 pb-3 border-b"
        style={{ borderColor: 'var(--border-light)' }}
      >
        <h2 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
          {t('chat.title')}
        </h2>
        <div className="flex items-center gap-1.5">
          {messages.length > 0 && (
            <button
              onClick={() => {
                const md = formatConversationAsMarkdown(messages)
                downloadAsMarkdown(md)
              }}
              className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium transition-all hover:scale-105"
              style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}
              title="Export conversation"
            >
              <Download size={12} />
            </button>
          )}
          <button
            onClick={() => createConversation()}
            className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-medium transition-all hover:scale-105"
            style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}
          >
            <Plus size={12} />
            {t('chat.newChat')}
          </button>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: 'var(--accent-light)' }}
            >
              <Sparkles size={22} style={{ color: 'var(--accent)' }} />
            </div>
            <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
              {t('chat.noMessages')}
            </p>

            {/* 추천 질문 */}
            {papers.length > 0 && (
              <div className="w-full space-y-1.5">
                {suggestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(q)}
                    className="w-full text-left px-3 py-2.5 rounded-xl text-xs transition-all hover:scale-[0.99]"
                    style={{
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border-light)',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} onFollowUpClick={handleSend} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* 입력 영역 */}
      <div className="p-3 pt-0">
        <div
          className="flex items-end gap-2 rounded-xl p-2"
          style={{
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-color)',
          }}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t('chat.placeholder')}
            rows={1}
            className="flex-1 resize-none outline-none text-sm py-1 px-1 bg-transparent"
            style={{
              color: 'var(--text-primary)',
              maxHeight: '120px',
            }}
            disabled={isStreaming}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isStreaming}
            className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all disabled:opacity-30 hover:scale-105"
            style={{
              background: input.trim() ? 'var(--accent)' : 'var(--border-color)',
              color: 'white',
            }}
          >
            {isStreaming ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Send size={14} />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
