import { expect, test } from '@playwright/test';

test('comparison controls and categories fit the sidebar at desktop and mobile widths', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /Local folder/ }).click();
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.getByRole('combobox', { name: 'Target revision' })).toBeVisible();
  await page.getByRole('button', { name: 'Compare', exact: true }).click();

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
