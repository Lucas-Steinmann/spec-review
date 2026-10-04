import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  plugins: [svelte()],
  base: '/',
  build: {
    outDir: fileURLToPath(new URL('../src/spec_review/webui', import.meta.url)),
    emptyOutDir: true,
    assetsDir: 'assets',
  },
});
