import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/movies': {
        target: 'http://3.86.188.48:3001',
        changeOrigin: true
      },
      '/api/rooms': {
        target: 'http://3.86.188.48:3002',
        changeOrigin: true
      },
      '/api/reservations': {
        target: 'http://3.86.188.48:3003',
        changeOrigin: true
      },
      '/api/users': {
        target: 'http://3.86.188.48:3003',
        changeOrigin: true
      },
      '/api/payments': {
        target: 'http://3.86.188.48:3003',
        changeOrigin: true
      },
      '/api/showtimes': {
        target: 'http://3.86.188.48:3004',
        changeOrigin: true
      },
      '/api/book-ticket': {
        target: 'http://3.86.188.48:3004',
        changeOrigin: true
      },
      '/api/user-dashboard': {
        target: 'http://3.86.188.48:3004',
        changeOrigin: true
      },
      '/api/movie-details': {
        target: 'http://3.86.188.48:3004',
        changeOrigin: true
      },
      '/api/genres': {
        target: 'http://3.86.188.48:3001',
        changeOrigin: true
      },
      '/api/schedules': {
        target: 'http://3.86.188.48:3002',
        changeOrigin: true
      }
    }
  }
})
