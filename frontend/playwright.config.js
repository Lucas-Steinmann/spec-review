import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'node:url';

const projectRoot = fileURLToPath(new URL('..', import.meta.url));

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: [
    {
      command: 'uv run --no-sync --project . python -m spec_review.cli --web --repo . --spec-dir spec --port 8765',
      cwd: projectRoot,
      env: { UV_CACHE_DIR: process.env.UV_CACHE_DIR || '/tmp/spec-review-uv-cache' },
      url: 'http://127.0.0.1:8765/api/status',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: 'npm run dev -- --strictPort',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
  ],
});
