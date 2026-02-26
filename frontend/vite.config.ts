import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '')

	return {
		plugins: [react(), tsconfigPaths()],
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
		},
		test: {
			environment: 'jsdom',
			globals: true,
			setupFiles: ['./src/tests/setup.ts'],
		}
	}
}) 