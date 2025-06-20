// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'; // <-- ДОБАВЬТЕ ЭТОТ ИМПОРТ

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: { // <-- НАЧАЛО НОВОГО БЛОКА
    alias: {
      '~': path.resolve(__dirname, './src'),
    },
  }, // <-- КОНЕЦ НОВОГО БЛОКА
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})