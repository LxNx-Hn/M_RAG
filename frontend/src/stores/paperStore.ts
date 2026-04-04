import { create } from 'zustand'
import type { Paper } from '@/types/paper'
import type { CollectionInfo } from '@/types/api'

interface PaperState {
  papers: Paper[]
  collections: CollectionInfo[]
  activePaperId: string | null
  activePage: number
  zoom: number
  uploading: boolean
  setPapers: (papers: Paper[]) => void
  setCollections: (cols: CollectionInfo[]) => void
  addPaper: (paper: Paper) => void
  removePaper: (docId: string) => void
  setActivePaper: (docId: string | null) => void
  setActivePage: (page: number) => void
  setZoom: (zoom: number) => void
  setUploading: (v: boolean) => void
}

export const usePaperStore = create<PaperState>((set) => ({
  papers: [],
  collections: [],
  activePaperId: null,
  activePage: 1,
  zoom: 1.0,
  uploading: false,

  setPapers: (papers) => set({ papers }),
  setCollections: (collections) => set({ collections }),
  addPaper: (paper) => set((s) => ({ papers: [...s.papers, paper] })),
  removePaper: (docId) => set((s) => ({
    papers: s.papers.filter((p) => p.doc_id !== docId),
    activePaperId: s.activePaperId === docId ? null : s.activePaperId,
  })),
  setActivePaper: (docId) => set({ activePaperId: docId, activePage: 1 }),
  setActivePage: (page) => set({ activePage: page }),
  setZoom: (zoom) => set({ zoom: Math.max(0.5, Math.min(3, zoom)) }),
  setUploading: (uploading) => set({ uploading }),
}))
