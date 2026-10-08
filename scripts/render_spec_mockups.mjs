#!/usr/bin/env node
import { createRequire } from 'node:module';
import { mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('../frontend/node_modules/playwright');
const root = resolve(import.meta.dirname, '..');
const source = resolve(root, 'spec/mockups/src');
const output = resolve(root, 'spec/mockups/rendered');
const mockups = [['terminal-workspace', 1452, 857], ['comparison-workspace', 1440, 900], ['browser-workspace', 1440, 900]];

await mkdir(output, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || '/usr/bin/chromium' });
try {
  for (const [name, width, height] of mockups) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
    await page.goto(`file://${resolve(source, `${name}.html`)}`);
    await page.screenshot({ path: resolve(output, `${name}.png`), fullPage: true });
    await page.close();
  }
} finally { await browser.close(); }
