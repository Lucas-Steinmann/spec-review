#!/usr/bin/env node
import { createRequire } from 'node:module';
import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('../frontend/node_modules/playwright');
const root = resolve(import.meta.dirname, '..');
const source = resolve(root, 'spec/mockups/src');
const output = resolve(root, 'spec/mockups/rendered');
const mockups = [
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
} finally { await browser.close(); }
