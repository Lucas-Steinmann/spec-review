import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  plugins: [svelte()],
  base: '/',
  server: {
    host: '127.0.0.1',
    proxy: {
      '/api': process.env.SPEC_REVIEW_API_URL || 'http://127.0.0.1:8765',
    },
  },
  build: {
    outDir: fileURLToPath(new URL('./dist', import.meta.url)),
    emptyOutDir: true,
    assetsDir: 'assets',
  },
});
