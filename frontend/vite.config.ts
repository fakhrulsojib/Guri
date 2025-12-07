import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '')

	return {
		plugins: [react()],
		server: {
			host: '0.0.0.0',
			port: 3000,
			allowedHosts: ['fakhrulsojib.mooo.com'],
			proxy: mode === 'development' ? {
				'/api': {
					target: 'http://backend:8000',
					changeOrigin: true,
					secure: false,
					ws: true
				},
				'/auth': {
					target: 'http://backend:8000',
					changeOrigin: true,
					secure: false,
				}
			} : undefined
		},
		define: {
			__MODE__: JSON.stringify(mode)
		}
	}
}) 