import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// Read config for base path

let base = '/';
let apiPrefix = '/api';
try {
  const configPath = path.resolve(__dirname, '..', 'config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const subDir = (config.deployment.subDir || '').replace(/^\/+/g, '').replace(/\/+$/g, '');
  base = subDir ? `/${subDir}/` : '/';
  apiPrefix = base + 'api';
} catch (e) {
  console.warn('Could not read config.json, using default base path "/"');
}

export default defineConfig({
  plugins: [react()],
  base: base,
  server: {
    port: 3000,
    proxy: {
      [apiPrefix]: {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => {
          // Remove the base + 'api' prefix (e.g., /testing/api) from the start
          const prefix = apiPrefix.endsWith('/') ? apiPrefix : apiPrefix + '/';
          const regex = new RegExp(`^${prefix}`);
          const rewritten = path.replace(regex, '/');
          // eslint-disable-next-line no-console
          console.log(`[vite-proxy] ${path} -> ${rewritten}`);
          return rewritten;
        },
      },
    },
  },
  build: {
    // Ensure correct base path for production
    outDir: 'dist'
  }
})
