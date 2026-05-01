import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // 不需要 rewrite，FastAPI 路由就是 /api/...
      }
    }
  },
  build: {
    outDir: 'dist',      // 构建产物输出到 dist/
    emptyOutDir: true,
  }
})
