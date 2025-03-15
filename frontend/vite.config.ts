import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'node:path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(process.cwd(), './src'),
    },
  },
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' },
    // 忽略类型错误
    tsconfigRaw: JSON.stringify({
      compilerOptions: {
        skipLibCheck: true,
        noImplicitAny: false,
      }
    })
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/api/events': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('SSE代理错误 (/api/events):', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('SSE代理请求 (/api/events):', req.url);
          });
          proxy.on('proxyRes', (_proxyRes, req, _res) => {
            console.log('SSE代理响应 (/api/events):', req.url);
          });
        }
      },
      '/events': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/events/, '/api/events'),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('SSE代理错误 (/events):', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('SSE代理请求 (/events):', req.url);
          });
          proxy.on('proxyRes', (_proxyRes, req, _res) => {
            console.log('SSE代理响应 (/events):', req.url);
          });
        }
      }
    }
  }
}) 