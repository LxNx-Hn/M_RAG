export interface Paper {
  doc_id: string
  title: string
  total_pages: number
  num_chunks: number
  sections: Record<string, number>
  filename?: string
}

export type SectionType =
  | 'abstract'
  | 'introduction'
  | 'method'
  | 'result'
  | 'conclusion'
  | 'references'
  | 'other'

export const SECTION_COLORS: Record<string, string> = {
  abstract: 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-300',
  introduction: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
  method: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
  result: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  conclusion: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300',
  references: 'bg-slate-100 text-slate-600 dark:bg-slate-800/50 dark:text-slate-400',
  other: 'bg-gray-100 text-gray-600 dark:bg-gray-800/50 dark:text-gray-400',
}
