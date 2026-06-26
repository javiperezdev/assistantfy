import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: { 
      '/API': { // Make frontend think that data comes from his own port (when making request with '/API')
        target: 'http://localhost:8000',
        changeOrigin: true // backend believes request is coming from his wame port
      }
    }
  }
})
