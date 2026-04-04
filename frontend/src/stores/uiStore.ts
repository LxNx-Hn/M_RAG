import { create } from 'zustand'
import i18n from 'i18next'

interface UIState {
  darkMode: boolean
  language: 'ko' | 'en'
  leftPanelOpen: boolean
  rightPanelOpen: boolean
  mobileActivePanel: 'left' | 'center' | 'right'
  toggleDarkMode: () => void
  setLanguage: (lang: 'ko' | 'en') => void
  toggleLeftPanel: () => void
  toggleRightPanel: () => void
  setMobileActivePanel: (panel: 'left' | 'center' | 'right') => void
}

export const useUIStore = create<UIState>((set) => ({
  darkMode: localStorage.getItem('darkMode') === 'true',
  language: (localStorage.getItem('language') as 'ko' | 'en') || 'ko',
  leftPanelOpen: true,
  rightPanelOpen: true,
  mobileActivePanel: 'center',

  toggleDarkMode: () =>
    set((state) => {
      const next = !state.darkMode
      localStorage.setItem('darkMode', String(next))
      if (next) document.documentElement.classList.add('dark')
      else document.documentElement.classList.remove('dark')
      return { darkMode: next }
    }),

  setLanguage: (lang) => {
    localStorage.setItem('language', lang)
    i18n.changeLanguage(lang) // 실시간 언어 전환 (새로고침 불필요)
    set({ language: lang })
  },

  toggleLeftPanel: () => set((s) => ({ leftPanelOpen: !s.leftPanelOpen })),
  toggleRightPanel: () => set((s) => ({ rightPanelOpen: !s.rightPanelOpen })),
  setMobileActivePanel: (panel) => set({ mobileActivePanel: panel }),
}))
