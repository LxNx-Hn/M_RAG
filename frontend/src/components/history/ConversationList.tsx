import { useTranslation } from 'react-i18next'
import { MessageSquare } from 'lucide-react'
import { useChatStore } from '@/stores/chatStore'

export default function ConversationList() {
  const { t } = useTranslation()
  const { conversations, activeConversationId, setActiveConversation } = useChatStore()

  if (conversations.length === 0) {
    return (
      <div className="p-4 text-center">
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
          {t('history.empty')}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-1 p-2">
      {conversations.map((conv) => (
        <button
          key={conv.id}
          onClick={() => setActiveConversation(conv.id)}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-all group"
          style={{
            background: activeConversationId === conv.id ? 'var(--accent-light)' : 'transparent',
            color: activeConversationId === conv.id ? 'var(--accent)' : 'var(--text-secondary)',
          }}
        >
          <MessageSquare size={14} className="shrink-0" />
          <span className="text-xs truncate flex-1">{conv.title}</span>
          <span className="text-[10px] shrink-0" style={{ color: 'var(--text-muted)' }}>
            {conv.messages.length}
          </span>
        </button>
      ))}
    </div>
  )
}
