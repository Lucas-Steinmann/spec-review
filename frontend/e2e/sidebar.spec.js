import { expect, test } from '@playwright/test';
import { fileURLToPath } from 'node:url';

test.beforeEach(async ({ page }) => {
  const root = fileURLToPath(new URL('../..', import.meta.url)).replace(/\/$/, '');
  await page.addInitScript((root) => { localStorage.setItem('spec-review-repositories', JSON.stringify([{ source: 'local', id: 'fixture', root, spec_dir: 'spec' }])); }, root);
});

test('comparison controls and categories fit the sidebar at desktop and mobile widths', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.repo-sidebar button').first()).toContainText('spec-review');
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.getByRole('combobox', { name: 'Target revision' })).toBeVisible();
  await page.getByRole('combobox', { name: 'Review or compare' }).selectOption('compare');
  await page.getByRole('button', { name: 'Apply revision' }).click();

  const checkbox = page.getByRole('checkbox', { name: 'Changes only' });
  await expect(checkbox).toBeVisible();
  const categoryButtons = page.locator('.category-list button');
  await expect(categoryButtons.first()).toBeVisible();

  for (const viewport of [{ width: 1280, height: 900 }, { width: 420, height: 900 }]) {
    await page.setViewportSize(viewport);
    const layout = await page.locator('.sidebar').evaluate((sidebar) => {
      const input = sidebar.querySelector('.checkbox input');
      const label = input.parentElement;
      const text = [...label.childNodes].find((node) => node.nodeType === Node.TEXT_NODE);
      const range = document.createRange();
      range.selectNode(text);
      const inputRect = input.getBoundingClientRect();
      const textRect = range.getBoundingClientRect();
      const list = sidebar.querySelector('.category-list');
      const listRect = list.getBoundingClientRect();
      const buttons = [...list.querySelectorAll('button')];
      return {
        checkboxWidth: inputRect.width,
        labelGap: textRect.left - inputRect.right,
        horizontalOverflow: list.scrollWidth - list.clientWidth,
        buttonsStayInside: buttons.every((button) => button.getBoundingClientRect().right <= listRect.right + 1),
        allButtonsVisible: buttons.every((button) => button.getBoundingClientRect().width > 0),
      };
    });

    expect(layout.checkboxWidth).toBeLessThan(30);
    expect(layout.labelGap).toBeGreaterThanOrEqual(5);
    expect(layout.labelGap).toBeLessThan(20);
    expect(layout.horizontalOverflow).toBeLessThanOrEqual(1);
    expect(layout.buttonsStayInside).toBe(true);
    expect(layout.allButtonsVisible).toBe(true);
  }

  const requirements = categoryButtons.filter({ hasText: 'Requirement' });
  await requirements.click();
  await expect(requirements).toHaveClass(/active/);
});

test('the real server adds a local folder through the browser and reviews its files', async ({ page }) => {
  const root = fileURLToPath(new URL('../..', import.meta.url)).replace(/\/$/, '');
  await page.addInitScript(() => localStorage.removeItem('spec-review-repositories'));
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Add a workspace' })).toBeVisible();
  await page.getByRole('button', { name: 'Add repository', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Add repository', exact: true });
  await expect(dialog.getByRole('button', { name: 'Go', exact: true })).toBeEnabled();
  await dialog.getByRole('textbox', { name: 'Folder path' }).fill(root);
  await dialog.getByRole('button', { name: 'Go', exact: true }).click();
  await expect(dialog.locator('.folder-browser')).toContainText('spec');
  await dialog.getByRole('button', { name: 'Add repository', exact: true }).click();
  await expect(page.locator('.repo-entry')).toHaveCount(1);
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.locator('.document-list')).toContainText('GOAL-001');
});
