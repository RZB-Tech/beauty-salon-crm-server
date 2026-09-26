import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    server: {
      host: true,
      // Telegram opens mini apps over HTTPS only - for local testing, tunnel this
      // port (cloudflared, ngrok, ...) and give BotFather the tunnel URL
      allowedHosts: true,
      proxy: {
        '/api': { target: env.VITE_DEV_PROXY_TARGET || 'http://localhost:8000', changeOrigin: true },
      },
    },
  }
})
