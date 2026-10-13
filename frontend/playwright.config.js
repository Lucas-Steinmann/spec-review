import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'node:url';

const projectRoot = fileURLToPath(new URL('..', import.meta.url));

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5179',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'], launchOptions: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } : {} } },
  ],
  webServer: [
    {
      command: 'uv run --no-sync --project . python -m spec_review.cli --web --port 8876',
      cwd: projectRoot,
      env: { UV_CACHE_DIR: process.env.UV_CACHE_DIR || '/tmp/spec-review-uv-cache' },
      url: 'http://127.0.0.1:8876/api/status',
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: 'npm run dev -- --strictPort --port 5179',
      env: { SPEC_REVIEW_API_URL: 'http://127.0.0.1:8876' },
      url: 'http://127.0.0.1:5179',
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
