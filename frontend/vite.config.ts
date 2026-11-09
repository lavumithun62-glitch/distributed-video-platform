
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/upload': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/orchestrator': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/thumbnail': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/delivery': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
