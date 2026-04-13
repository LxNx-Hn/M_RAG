import type { Message } from '@/types/chat'

/** 단일 메시지를 마크다운으로 포맷 */
export function formatMessageAsMarkdown(msg: Message): string {
  const role = msg.role === 'user' ? 'User' : 'M-RAG'
  let md = `**${role}**\n\n${msg.content}\n`

  if (msg.route) {
    md = `**${role}** (Route ${msg.route.route}: ${msg.route.route_name})\n\n${msg.content}\n`
  }

  if (msg.sources && msg.sources.length > 0) {
    md += '\n---\n**Sources:**\n'
    msg.sources.forEach((src, i) => {
      md += `${i + 1}. [${src.section_type}] p.${src.page} — ${src.content.slice(0, 80)}...\n`
    })
  }

  return md
}

/** 전체 대화를 마크다운으로 포맷 */
export function formatConversationAsMarkdown(messages: Message[]): string {
  const header = `# M-RAG Conversation\n\n*Exported: ${new Date().toLocaleString()}*\n\n---\n\n`
  const body = messages.map(formatMessageAsMarkdown).join('\n---\n\n')
  return header + body
}

/** 클립보드에 복사 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    return false
  }
}

/** 마크다운 파일로 다운로드 */
export function downloadAsMarkdown(content: string, filename?: string) {
  const fname = filename || `m-rag-export-${Date.now()}.md`
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = fname
  a.click()
  URL.revokeObjectURL(url)
}
