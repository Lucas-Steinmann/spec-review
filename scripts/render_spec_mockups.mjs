#!/usr/bin/env node
import { createRequire } from 'node:module';
import { mkdir, readFile, stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { spawnSync } from 'node:child_process';
import { installDialogFixture } from '../spec/mockups/src/browser-dialogs.mjs';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('../frontend/node_modules/playwright');
const root = resolve(import.meta.dirname, '..');
const output = resolve(root, 'spec/mockups/rendered');

async function serve(directory) {
  const server = createServer(async (request, response) => {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const path = resolve(directory, `.${pathname}`);
    if (path !== directory && !path.startsWith(`${directory}/`)) { response.writeHead(404).end(); return; }
    try {
      const file = (await stat(path)).isDirectory() ? resolve(path, 'index.html') : path;
      const type = file.endsWith('.css') ? 'text/css'
        : file.endsWith('.js') ? 'text/javascript'
          : file.endsWith('.json') ? 'application/json'
            : file.endsWith('.svg') ? 'image/svg+xml'
              : file.endsWith('.woff2') ? 'font/woff2' : 'text/html';
      response.writeHead(200, { 'Content-Type': type }).end(await readFile(file));
    } catch { response.writeHead(404).end(); }
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return { server, url: `http://127.0.0.1:${server.address().port}` };
}

async function closeServer(server) { await new Promise((resolve) => server.close(resolve)); }

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || '/usr/bin/chromium' });
try {
  // Export the current Textual screen and rasterize it with the same Chromium renderer.
  const terminalSvg = resolve('/tmp', 'spec-review-terminal-workspace.svg');
  const terminalExport = spawnSync('uv', ['run', 'python', 'scripts/render_terminal_mockup.py', terminalSvg], {
    cwd: root,
    encoding: 'utf8',
    env: { ...process.env, UV_CACHE_DIR: process.env.UV_CACHE_DIR || '/tmp/spec-review-uv-cache' },
  });
  if (terminalExport.status !== 0) throw new Error(terminalExport.stderr || terminalExport.stdout || 'Terminal mockup export failed');
  const terminalPreview = await browser.newPage({ viewport: { width: 1452, height: 857 }, deviceScaleFactor: 1 });
  const terminalMarkup = (await readFile(terminalSvg, 'utf8'))
    .replace(/url\("https:\/\/[^\"]+\.woff2"\)\s*format\("woff2"\),?/g, '');
  await terminalPreview.setContent(`<style>html,body{width:100%;height:100%;margin:0;overflow:hidden}svg.rich-terminal{width:100vw;height:100vh}</style>${terminalMarkup}`);
  await terminalPreview.screenshot({ path: resolve(output, 'terminal-workspace.png'), timeout: 0 });
  await terminalPreview.close();

  // Browser mockups are Storybook stories of App.svelte, the application itself.
  const storybook = await serve(resolve(root, 'frontend/storybook-static'));
  try {
    const previews = [
      ['browser--revision-comparison', 'comparison-workspace', 'paper', 1440, 900, '.diff-columns'],
      ['browser--local-worktrees', 'browser-worktrees-paper', 'paper', 1440, 900, '.pull-card'],
      ['browser--git-hub-overview', 'browser-workspace-paper', 'paper', 1440, 900, '.pull-card'],
      ['browser--git-hub-overview', 'browser-workspace-dark', 'dark', 1440, 900, '.pull-card'],
      ['browser--git-hub-overview', 'browser-workspace-paper-mobile', 'paper', 430, 932, '.overview-layout'],
      ['browser--git-hub-overview', 'browser-workspace-dark-mobile', 'dark', 430, 932, '.overview-layout'],
      ['browser--revision-comparison', 'browser-review-paper', 'paper', 1440, 900, '.diff-columns'],
      ['browser--revision-comparison', 'browser-review-dark', 'dark', 1440, 900, '.diff-columns'],
      ['browser--revision-comparison', 'browser-review-paper-mobile', 'paper', 430, 932, '.diff-columns'],
      ['browser--revision-comparison', 'browser-review-dark-mobile', 'dark', 430, 932, '.diff-columns'],
    ];
    for (const [id, name, theme, width, height, selector] of previews) {
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
      await page.goto(`${storybook.url}/iframe.html?id=${id}&viewMode=story&globals=theme%3A${theme}`);
      await page.locator(selector).first().waitFor();
      await page.evaluate(() => document.activeElement instanceof HTMLElement && document.activeElement.blur());
      await page.screenshot({ path: resolve(output, `${name}.png`), fullPage: true });
      await page.close();
    }
  } finally { await closeServer(storybook.server); }

  const app = await serve(resolve(root, 'frontend/dist'));
  try {
    for (const theme of ['paper', 'dark']) {
      for (const width of [1280, 360]) {
        const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
        await installDialogFixture(page, theme);
        await page.goto(app.url);
        await page.getByRole('button', { name: 'Add repository', exact: true }).click();
        const dialog = page.getByRole('dialog', { name: 'Add repository' });
        await dialog.getByRole('button', { name: 'Go', exact: true }).waitFor();
        await page.waitForFunction(() => document.querySelector('dialog[open] .folder-browser'));
        await page.screenshot({ path: resolve(output, `browser-add-${theme}${width === 360 ? '-mobile' : ''}.png`) });
        await page.keyboard.press('Escape');
        if (width === 360) {
          await page.getByRole('button', { name: 'Settings', exact: true }).click();
          await page.screenshot({ path: resolve(output, `browser-settings-${theme}-mobile.png`) });
        }
        await page.close();
      }
    }
  } finally { await closeServer(app.server); }
} finally { await browser.close(); }
