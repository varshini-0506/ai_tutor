import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  preview: {
    host: '0.0.0.0',
    port: process.env.PORT || 3000,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'ai-tutor-frontend-kkne.onrender.com',
      '.onrender.com' // Allow all onrender.com subdomains
    ]
  }
})
