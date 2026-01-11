import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Read config for base path
let base = '/'
try {
  const configPath = path.resolve(__dirname, '..', 'config.json')
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'))
  const subDir = config.deployment.subDir || ''
  base = subDir ? `/${subDir}` : '/'
} catch (e) {
  console.warn('Could not read config.json, using default base path "/"')
}

export default defineConfig({
  plugins: [react()],
  base: base,
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    // Ensure correct base path for production
    outDir: 'dist'
  }
})
