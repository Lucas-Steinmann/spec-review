import { expect, test } from '@playwright/test';
import { installDialogFixture } from '../../spec/mockups/src/browser-dialogs.mjs';

const sizes = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'narrow', width: 360, height: 800 },
  { name: 'small', width: 320, height: 640 },
];

for (const theme of ['paper', 'dark']) {
  for (const size of sizes) {
    test(`Add dialog controls fit without overlap in ${theme} at ${size.name}`, async ({ page }, testInfo) => {
      await page.setViewportSize(size);
      await installDialogFixture(page, theme);
      await page.goto('/');
      const opener = page.getByRole('button', { name: 'Add repository', exact: true });
      await opener.click();
      const dialog = page.getByRole('dialog', { name: 'Add repository', exact: true });
      const source = dialog.getByRole('combobox', { name: 'Source type' });
      const path = dialog.getByRole('textbox', { name: 'Folder path' });
      const go = dialog.getByRole('button', { name: 'Go', exact: true });
      await expect(source).toBeFocused();
      await expect(go).toBeEnabled();
      const pathBox = await path.boundingBox();
      const goBox = await go.boundingBox();
      expect(pathBox.width).toBeGreaterThan(160);
      expect(pathBox.height).toBeGreaterThanOrEqual(36);
      expect(goBox.width).toBeLessThan(80);
      expect(pathBox.x + pathBox.width + 6).toBeLessThanOrEqual(goBox.x);
      expect(Math.abs(pathBox.y - goBox.y)).toBeLessThan(2);
      const font = await go.evaluate((node) => parseFloat(getComputedStyle(node).fontSize));
      expect(font).toBeLessThanOrEqual(14);
      const layout = await dialog.evaluate((node) => {
        const modal = node.getBoundingClientRect();
        const fields = [...node.querySelectorAll('input, select')].map((field) => {
          const control = field.getBoundingClientRect();
          const label = field.closest('label').querySelector('.field-label').getBoundingClientRect();
          return { width: control.width, height: control.height, labelBottom: label.bottom, top: control.top, inside: control.left >= modal.left && control.right <= modal.right };
        });
        return { fields, inside: modal.left >= 0 && modal.right <= innerWidth && modal.top >= 0 && modal.bottom <= innerHeight, overflow: node.scrollWidth - node.clientWidth };
      });
      expect(layout.inside).toBe(true);
      expect(layout.overflow).toBeLessThanOrEqual(1);
      for (const field of layout.fields) {
        expect(field.height).toBeGreaterThanOrEqual(36);
        expect(field.inside).toBe(true);
        expect(field.labelBottom + 4).toBeLessThanOrEqual(field.top);
      }
      const add = dialog.getByRole('button', { name: 'Add repository', exact: true });
      const cancel = dialog.getByRole('button', { name: 'Cancel', exact: true });
      await add.scrollIntoViewIfNeeded();
      const addBox = await add.boundingBox();
      const cancelBox = await cancel.boundingBox();
      expect(cancelBox.x + cancelBox.width + 4).toBeLessThanOrEqual(addBox.x);
      const primary = await add.evaluate((node) => ({ background: getComputedStyle(node).backgroundColor, border: getComputedStyle(node).borderColor }));
      const secondary = await cancel.evaluate((node) => getComputedStyle(node).backgroundColor);
      expect(primary.background).not.toBe(secondary);
      await page.screenshot({ path: testInfo.outputPath('add-dialog.png') });
      await source.selectOption('gh');
      const repository = dialog.getByRole('combobox', { name: 'Repository', exact: true });
      await expect(repository).toHaveValue('optograph/companion-app');
      expect((await repository.boundingBox()).height).toBeGreaterThanOrEqual(36);
      await page.keyboard.press('Escape');
      await expect(dialog).not.toBeVisible();
      await expect(opener).toBeFocused();
    });
  }
}

test('Settings uses a compact close control, matching fields, and restores keyboard focus', async ({ page }, testInfo) => {
  await installDialogFixture(page, 'dark');
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto('/');
  const opener = page.getByRole('button', { name: 'Settings', exact: true });
  await opener.click();
  const dialog = page.getByRole('dialog', { name: 'Settings', exact: true });
  await expect(dialog.getByRole('combobox', { name: 'Appearance' })).toBeFocused();
  const close = dialog.getByRole('button', { name: 'Close settings' });
  const closeBox = await close.boundingBox();
  expect(closeBox.width).toBe(32);
  expect(closeBox.height).toBe(32);
  const done = dialog.getByRole('button', { name: 'Done', exact: true });
  expect((await done.boundingBox()).width).toBeLessThan(120);
  await page.screenshot({ path: testInfo.outputPath('settings-dialog.png') });
  await done.click();
  await expect(opener).toBeFocused();
});

test('loading and long errors preserve the narrow dialog layout and keyboard access', async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 360, height: 640 });
  await installDialogFixture(page, 'paper');
  let release;
  const pending = new Promise((resolve) => { release = resolve; });
  await page.route('**/api/local/folders?*', async (route) => {
    await pending;
    await route.fulfill({ status: 400, contentType: 'application/json', body: JSON.stringify({ error: `Cannot read folder: /${'very-long-folder-name-'.repeat(12)}` }) });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Add repository', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Add repository', exact: true });
  await expect(dialog.getByRole('status')).toBeVisible();
  await expect(dialog.getByRole('button', { name: 'Go', exact: true })).toBeDisabled();
  const close = dialog.getByRole('button', { name: 'Close add repository', exact: true });
  await close.focus();
  await page.keyboard.press('Shift+Tab');
  await expect(dialog.getByRole('button', { name: 'Cancel', exact: true })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(close).toBeFocused();
  for (let index = 0; index < 8; index += 1) {
    await page.keyboard.press('Tab');
    expect(await dialog.evaluate((node) => node.contains(document.activeElement))).toBe(true);
  }
  release();
  await expect(dialog.getByRole('alert')).toContainText('Cannot read folder');
  expect(await dialog.evaluate((node) => node.scrollWidth - node.clientWidth)).toBeLessThanOrEqual(1);
  await page.screenshot({ path: testInfo.outputPath('add-error.png') });
  await dialog.getByRole('combobox', { name: 'Source type' }).selectOption('gh');
  await expect(dialog.getByRole('combobox', { name: 'Repository' })).toHaveValue('optograph/companion-app');
  await expect(dialog.getByRole('alert')).toHaveCount(0);
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
});

test('canceling Add discards a pending validation response', async ({ page }) => {
  await installDialogFixture(page);
  let release;
  const pending = new Promise((resolve) => { release = resolve; });
  await page.route('**/api/local/validate?*', async (route) => {
    await pending;
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify({ root: '/home/reviewer', spec_dir: 'spec', is_git: false }) });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Add repository', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Add repository' });
  await dialog.getByRole('button', { name: 'Add repository', exact: true }).click();
  await expect(dialog.getByRole('status')).toBeVisible();
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(page.getByRole('button', { name: 'Add repository', exact: true })).toBeFocused();
  const response = page.waitForResponse((response) => new URL(response.url()).pathname === '/api/local/validate');
  release();
  await (await response).finished();
  await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(resolve)));
  await expect(page.locator('.repo-entry')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Add a workspace' })).toBeVisible();
});
