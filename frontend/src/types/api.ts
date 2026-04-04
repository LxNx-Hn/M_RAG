/* Backend API 스키마 미러 */

export interface HealthResponse {
  status: string
  modules_loaded: boolean
  gpu_available: boolean
  collections: string[]
}

export interface PaperInfo {
  doc_id: string
  title: string
  total_pages: number
  num_chunks: number
  sections: Record<string, number>
}

export interface UploadResponse {
  success: boolean
  paper: PaperInfo | null
  message: string
}

export interface SourceDocument {
  chunk_id: string
  content: string
  section_type: string
  doc_id: string
  page: number
  score: number
  bbox?: number[][]
}

export interface RouteInfo {
  route: string
  route_name: string
  section_filter: string | null
  confidence: number
}

export interface QueryRequest {
  query: string
  collection_name?: string
  use_cad?: boolean
  cad_alpha?: number
  use_hyde?: boolean
  top_k?: number
  conversation_id?: string
}

export interface QueryResponse {
  answer: string
  route: RouteInfo
  sources: SourceDocument[]
  steps: Record<string, unknown>[]
  pipeline: string
}

export interface SearchRequest {
  query: string
  collection_name?: string
  section_filter?: string | null
  doc_id_filter?: string | null
  top_k?: number
}

export interface SearchResponse {
  results: SourceDocument[]
  total: number
  bm25_fitted: boolean
}

export interface CollectionInfo {
  name: string
  count: number
  doc_ids: string[]
}

export interface CollectionListResponse {
  collections: CollectionInfo[]
}

export interface CitationRequest {
  doc_id: string
  collection_name?: string
  max_citations?: number
}

export interface CitationItem {
  ref_id: string
  title: string
  authors: string
  year: string | null
  arxiv_id: string | null
  fetched: boolean
  has_pdf: boolean
}

export interface CitationResponse {
  citations: CitationItem[]
  fetched_count: number
  indexed_count: number
}

/* SSE 이벤트 */
export interface SSEMetadataEvent {
  route: RouteInfo
  sources: SourceDocument[]
  steps: Record<string, unknown>[]
}

export interface SSETokenEvent {
  token: string
}

export interface SSEDoneEvent {
  full_answer: string
}
