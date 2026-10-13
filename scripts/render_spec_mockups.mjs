#!/usr/bin/env node
import { createRequire } from 'node:module';
import { mkdir, readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { installDialogFixture } from '../spec/mockups/src/browser-dialogs.mjs';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('../frontend/node_modules/playwright');
const root = resolve(import.meta.dirname, '..');
const source = resolve(root, 'spec/mockups/src');
const output = resolve(root, 'spec/mockups/rendered');
const mockups = [
  ['browser-worktrees.html', 'browser-worktrees-paper', 'paper', 1440, 900],
  ['terminal-workspace.html', 'terminal-workspace', 'paper', 1452, 857],
  ['comparison-workspace.html', 'comparison-workspace', 'paper', 1440, 900],
  ['browser-workspace.html', 'browser-workspace-paper', 'paper', 1440, 900],
  ['browser-workspace.html', 'browser-workspace-dark', 'dark', 1440, 900],
  ['browser-workspace.html', 'browser-workspace-paper-mobile', 'paper', 430, 932],
  ['browser-workspace.html', 'browser-workspace-dark-mobile', 'dark', 430, 932],
  ['browser-review.html', 'browser-review-paper', 'paper', 1440, 900],
  ['browser-review.html', 'browser-review-dark', 'dark', 1440, 900],
  ['browser-review.html', 'browser-review-paper-mobile', 'paper', 430, 932],
  ['browser-review.html', 'browser-review-dark-mobile', 'dark', 430, 932],
];

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || '/usr/bin/chromium' });
try {
  for (const [html, name, theme, width, height] of mockups) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
    await page.goto(`file://${resolve(source, html)}#${theme}`);
    await page.screenshot({ path: resolve(output, `${name}.png`), fullPage: true });
    await page.close();
  }
  // Render dialog previews from the compiled application, not standalone approximations.
  const dist = resolve(root, 'frontend/dist');
  const server = createServer(async (request, response) => {
    const path = resolve(dist, `.${new URL(request.url, 'http://localhost').pathname}`);
    if (path !== dist && !path.startsWith(`${dist}/`)) { response.writeHead(404).end(); return; }
    try {
      const file = path === dist ? resolve(dist, 'index.html') : path;
      const type = file.endsWith('.css') ? 'text/css' : file.endsWith('.js') ? 'text/javascript' : 'text/html';
      response.writeHead(200, { 'Content-Type': type }).end(await readFile(file));
    } catch { response.writeHead(404).end(); }
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  try {
    for (const theme of ['paper', 'dark']) {
      for (const width of [1280, 360]) {
        const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
        await installDialogFixture(page, theme);
        await page.goto(`http://127.0.0.1:${server.address().port}`);
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
  } finally { await new Promise((resolve) => server.close(resolve)); }
} finally { await browser.close(); }
