import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('pdfjs-dist')) {
            return 'pdf-viewer'
          }
          if (id.includes('node_modules')) {
            if (
              id.includes(`${path.sep}react${path.sep}`) ||
              id.includes(`${path.sep}react-dom${path.sep}`) ||
              id.includes(`${path.sep}scheduler${path.sep}`)
            ) {
              return 'react-vendor'
            }
            return 'vendor'
          }
          return undefined
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
})
