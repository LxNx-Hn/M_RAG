import { create } from 'zustand'

interface UIState {
  darkMode: boolean
  leftPanelOpen: boolean
  rightPanelOpen: boolean
  mobileActivePanel: 'left' | 'center' | 'right'
  toggleDarkMode: () => void
  toggleLeftPanel: () => void
  toggleRightPanel: () => void
  setMobileActivePanel: (panel: 'left' | 'center' | 'right') => void
}

const getInitialDarkMode = (): boolean => {
  const stored = localStorage.getItem('darkMode')
  if (stored !== null) return stored === 'true'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export const useUIStore = create<UIState>((set) => ({
  darkMode: getInitialDarkMode(),
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


  toggleLeftPanel: () => set((s) => ({ leftPanelOpen: !s.leftPanelOpen })),
  toggleRightPanel: () => set((s) => ({ rightPanelOpen: !s.rightPanelOpen })),
  setMobileActivePanel: (panel) => set({ mobileActivePanel: panel }),
}))
