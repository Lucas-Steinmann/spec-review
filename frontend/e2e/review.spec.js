import { expect, test } from '@playwright/test';

const oldGoal = { id: 'GOAL-001', type: 'goal', title: 'Plan', path: 'spec/artifacts/goals/GOAL-001.yaml' };
const newGoal = { ...oldGoal };
const useCase = { id: 'UC-001', type: 'use_case', title: 'Review', path: 'spec/artifacts/use-cases/UC-001.yaml' };
const addedRequirement = { id: 'REQ-001', type: 'requirement', title: 'New requirement', path: 'spec/artifacts/requirements/REQ-001.yaml' };
const deletedDesign = { id: 'DES-001', type: 'design', title: 'Old design', path: 'spec/artifacts/design/DES-001.yaml' };
const categories = { goal: 'Goals', use_case: 'Use Cases', requirement: 'Requirements', design: 'Technical Design' };
const snapshot = (revision, goal = newGoal) => ({ revision, documents: { 'GOAL-001': goal, 'UC-001': useCase }, diagnostics: [], categories });
const comparison = (base = 'base', target = 'working tree') => ({
  base: snapshot(base, oldGoal), target: snapshot(target),
  changes: {
    'GOAL-001': { id: 'GOAL-001', status: 'changed', old: oldGoal, new: newGoal },
    'UC-001': { id: 'UC-001', status: 'unchanged', old: useCase, new: useCase },
    'REQ-001': { id: 'REQ-001', status: 'added', old: null, new: addedRequirement },
    'DES-001': { id: 'DES-001', status: 'deleted', old: deletedDesign, new: null },
  },
});
const section = (heading, text) => ({ heading, blocks: [{ kind: 'markdown', text, language: '' }] });

async function mockApi(page, answer) {
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    const result = answer(url, route.request());
    if (result === undefined) throw new Error(`Unexpected API request: ${url}`);
    await route.fulfill({ status: result.status || 200, contentType: 'application/json', body: JSON.stringify(result.body ?? result) });
  });
}

async function tabTo(page, locator) {
  for (let index = 0; index < 30; index += 1) {
    if (await locator.evaluate((element) => element === document.activeElement)) return;
    await page.keyboard.press('Tab');
  }
  await expect(locator).toBeFocused();
}

test('local overview loads without contacting gh until requested', async ({ page }) => {
  const paths = [];
  await mockApi(page, (url) => {
    paths.push(url.pathname);
    if (url.pathname === '/api/status') return { repo: '/tmp/sample', spec_dir: 'spec' };
    if (url.pathname === '/api/local/commits') return { branches: [], commits: [] };
    if (url.pathname === '/api/local/snapshot') return snapshot('working tree');
  });
  await page.goto('/');
  await expect(page.locator('.repo-sidebar')).toContainText('/tmp/sample');
  await expect(page.getByRole('button', { name: 'Open review' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.locator('.document-list')).toContainText('GOAL-001');
  expect(paths.every((path) => !path.startsWith('/api/gh/'))).toBe(true);
});

test('gh CLI repositories, saved overview, Actions, and pull comparison', async ({ page }) => {
  const loadedRevisions = [];
  await mockApi(page, (url) => {
    if (url.pathname === '/api/status') return { repo: '/tmp/sample', spec_dir: 'spec' };
    if (url.pathname === '/api/gh/account') return { login: 'reviewer' };
    if (url.pathname === '/api/gh/repos') return [{ full_name: 'owner/project', default_branch: 'main', private: true }];
    if (url.pathname === '/api/gh/overview') return [
      { number: 7, title: 'Improve review', head: 'head', head_ref: 'feature', base: 'base', base_ref: 'main', checks: 'success' },
      { number: 8, title: 'Checks hidden', head: 'other', head_ref: 'other', base: 'base', base_ref: 'main', checks: 'unavailable' },
    ];
    if (url.pathname === '/api/gh/branches') return [{ name: 'main', sha: 'main' }, { name: 'feature', sha: 'feature' }];
    if (url.pathname === '/api/gh/pulls') return [{ number: 7, title: 'Improve review', head: 'head', base: 'base' }];
    if (url.pathname === '/api/gh/commits') return [{ sha: 'head', subject: 'Head' }, { sha: 'base', subject: 'Base' }];
    if (url.pathname === '/api/gh/compare') return comparison(url.searchParams.get('base'), url.searchParams.get('target'));
    if (url.pathname === '/api/gh/snapshot') {
      loadedRevisions.push(url.searchParams.get('ref'));
      return snapshot(url.searchParams.get('ref'));
    }
  });
  await page.goto('/');
  await tabTo(page, page.getByRole('button', { name: 'Add', exact: true }));
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog', { name: 'Add GitHub repository' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('combobox', { name: 'Repository' })).toBeFocused();
  await tabTo(page, dialog.getByRole('button', { name: 'Add repository' }));
  await page.keyboard.press('Enter');
  await expect(page.locator('.repo-sidebar')).toContainText('owner/project');
  await expect(page.locator('.pull-card').first()).toContainText('Improve review');
  await expect(page.locator('.pull-card').first()).toContainText('success');
  await expect(page.locator('.pull-card').nth(1)).toContainText('Actions unavailable');
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.getByRole('combobox', { name: 'Target revision' })).toHaveValue('main');
  await expect.poll(() => loadedRevisions.at(-1)).toBe('main');
  await page.getByRole('combobox', { name: 'Target revision' }).selectOption('feature');
  await expect.poll(() => loadedRevisions.at(-1)).toBe('feature');
  await page.getByRole('combobox', { name: 'Target revision' }).selectOption('base');
  await expect.poll(() => loadedRevisions.at(-1)).toBe('base');
  expect(loadedRevisions).toEqual(['main', 'feature', 'base']);
  await page.getByRole('button', { name: /Overview/ }).click();
  await page.reload();
  await expect(page.locator('.repo-sidebar')).toContainText('owner/project');
  await expect(page.locator('.pull-card').first()).toContainText('Improve review');
  await page.locator('.pull-card').first().click();
  await expect(page.locator('.revision-summary')).toContainText('base → head');
  await expect(page.locator('.category-list button').first()).toContainText('★');
  await page.getByRole('combobox', { name: 'Target revision' }).selectOption('main');
  await expect(page.locator('.document-list')).toContainText('GOAL-001');
});

test('local selection remains available during a pending gh overview refresh', async ({ page }) => {
  let releaseOverview;
  const pending = new Promise((resolve) => { releaseOverview = resolve; });
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    let body;
    if (url.pathname === '/api/status') body = { repo: '/tmp/sample', spec_dir: 'spec' };
    else if (url.pathname === '/api/gh/account') body = { login: 'reviewer' };
    else if (url.pathname === '/api/gh/repos') body = [{ full_name: 'owner/project', default_branch: 'main', private: true }];
    else if (url.pathname === '/api/gh/overview') { await pending; body = []; }
    else throw new Error(`Unexpected API request: ${url}`);
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(body) });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Add', exact: true }).click();
  await page.getByRole('dialog', { name: 'Add GitHub repository' }).getByRole('button', { name: 'Add repository' }).click();
  await expect(page.getByRole('status')).toContainText('Loading pull requests');
  await page.getByRole('button', { name: /Local folder/ }).click();
  await expect(page.getByRole('button', { name: 'Open review' })).toBeVisible();
  releaseOverview();
  await expect(page.getByRole('button', { name: 'Open review' })).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('gh sign-in failure is explained at the browser boundary', async ({ page }) => {
  await mockApi(page, (url) => {
    if (url.pathname === '/api/status') return { repo: '/tmp/sample', spec_dir: 'spec' };
    if (url.pathname === '/api/gh/account') return { status: 400, body: { error: 'GitHub CLI is not authenticated; run `gh auth login`' } };
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Add', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('gh auth login');
  await expect(page.getByRole('dialog', { name: 'Add GitHub repository' })).not.toBeVisible();
  await expect(page.getByRole('button', { name: 'Open review' })).toBeVisible();
});

test('repository discovery keeps the local overview usable while gh responds', async ({ page }) => {
  let releaseAccount;
  const pending = new Promise((resolve) => { releaseAccount = resolve; });
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    let body;
    if (url.pathname === '/api/status') body = { repo: '/tmp/sample', spec_dir: 'spec' };
    else if (url.pathname === '/api/gh/account') { await pending; body = { login: 'reviewer' }; }
    else if (url.pathname === '/api/gh/repos') body = [{ full_name: 'owner/project', default_branch: 'main', private: true }];
    else throw new Error(`Unexpected API request: ${url}`);
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(body) });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Add', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('Loading GitHub repositories');
  await page.getByRole('button', { name: /Local folder/ }).click();
  await expect(page.getByRole('button', { name: 'Open review' })).toBeVisible();
  releaseAccount();
  await expect(page.getByRole('dialog', { name: 'Add GitHub repository' })).toBeVisible();
});

test('local revision selection, both working-tree directions, filter, and rendered diff', async ({ page }) => {
  const comparisons = [];
  await mockApi(page, (url) => {
    if (url.pathname === '/api/status') return { repo: '/tmp/sample', spec_dir: 'spec' };
    if (url.pathname === '/api/local/commits') return { branches: [], commits: [{ sha: 'target', subject: 'Target' }, { sha: 'base', subject: 'Base' }] };
    if (url.pathname === '/api/local/snapshot') return snapshot(url.searchParams.get('ref') || 'working tree');
    if (url.pathname === '/api/local/compare') {
      comparisons.push([url.searchParams.get('base'), url.searchParams.get('target')]);
      return comparison(url.searchParams.get('base') || 'working tree', url.searchParams.get('target') || 'working tree');
    }
    if (url.pathname === '/api/local/document') {
      const ref = url.searchParams.get('ref');
      const id = url.searchParams.get('id');
      if (id === 'UC-001') return { document: useCase, revision: ref || 'working tree', sections: [section('Description', 'Review use case')] };
      if (id === 'REQ-001') return { document: addedRequirement, revision: ref || 'working tree', sections: [section('Statement', 'New requirement text')] };
      if (id === 'DES-001') return { document: deletedDesign, revision: ref || 'working tree', sections: [section('Description', 'Old design text')] };
      const old = ref === 'base';
      return { document: old ? oldGoal : newGoal, revision: ref || 'working tree', sections: [section('Description', old ? 'The **old label** stays' : 'The **new label** stays')] };
    }
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.locator('.document-list')).toContainText('GOAL-001');
  await page.getByRole('combobox', { name: 'Target revision' }).selectOption('base');
  await page.getByRole('button', { name: 'Use Cases' }).click();
  await page.locator('.document-item', { hasText: 'UC-001' }).click();
  await expect(page.locator('.content-pane')).toContainText('Review use case');
  await page.getByRole('button', { name: 'Goals' }).click();
  const elapsed = await page.locator('.document-item', { hasText: 'GOAL-001' }).evaluate((button) => new Promise((resolve, reject) => {
    const pane = document.querySelector('.content-pane');
    const started = performance.now();
    const timeout = setTimeout(() => { observer.disconnect(); reject(new Error('Document did not render')); }, 1000);
    const observer = new MutationObserver(() => {
      if (pane.textContent.includes('old label')) {
        clearTimeout(timeout);
        observer.disconnect();
        resolve(performance.now() - started);
      }
    });
    observer.observe(pane, { subtree: true, childList: true, characterData: true });
    button.click();
  }));
  await expect(page.locator('.content-pane')).toContainText('old label');
  expect(elapsed).toBeLessThan(200);

  await page.getByRole('combobox', { name: 'Target revision' }).selectOption('');
  await page.getByRole('button', { name: 'Compare', exact: true }).click();
  await expect(page.locator('.category-list button').first()).toContainText('★');
  await page.locator('.document-item', { hasText: 'GOAL-001' }).click();
  await expect(page.locator('.diff-side')).toHaveCount(2);
  await expect(page.locator('.diff-side').first().locator('.changed-line .diff-text.removed')).toHaveText('old');
  await expect(page.locator('.diff-side').last().locator('.changed-line .diff-text.added')).toHaveText('new');
  await page.getByRole('button', { name: 'Requirements' }).click();
  await page.locator('.document-item', { hasText: 'REQ-001' }).click();
  await expect(page.locator('.diff-side').first()).toContainText('Document absent');
  await expect(page.locator('.diff-side').last()).toContainText('New requirement text');
  await page.getByRole('button', { name: 'Technical Design' }).click();
  await page.locator('.document-item', { hasText: 'DES-001' }).click();
  await expect(page.locator('.diff-side').first()).toContainText('Old design text');
  await expect(page.locator('.diff-side').last()).toContainText('Document absent');
  await page.getByRole('checkbox', { name: 'Changes only' }).check();
  await page.getByRole('button', { name: 'Use Cases' }).click();
  await expect(page.locator('.document-list')).toContainText('No documents');

  await page.getByRole('combobox', { name: 'Base revision' }).selectOption('');
  await page.getByRole('combobox', { name: 'Target revision' }).selectOption('base');
  await page.getByRole('button', { name: 'Compare', exact: true }).click();
  expect(comparisons).toEqual([['base', ''], ['', 'base']]);
});

test('browser document formatting, links, and diagram fallback', async ({ page }) => {
  await mockApi(page, (url) => {
    if (url.pathname === '/api/status') return { repo: '/tmp/sample', spec_dir: 'spec' };
    if (url.pathname === '/api/local/commits') return { branches: [], commits: [{ sha: 'base', subject: 'Base' }] };
    if (url.pathname === '/api/local/snapshot') return snapshot('working tree');
    if (url.pathname === '/api/local/document') {
      const id = url.searchParams.get('id');
      return {
        document: id === 'GOAL-001' ? newGoal : useCase, revision: 'working tree',
        sections: id === 'GOAL-001' ? [section('Statement', 'Destination')] : [
          section('Description', 'See [goal](GOAL-001), [choice](choice), and [missing](missing).'),
          section('Source', 'spec/sources/chat.md#Initial request'),
          section('Preconditions', '- First\n- Second'),
          section('Postconditions', '- Done'),
          { heading: 'Diagram', blocks: [{ kind: 'diagram', text: 'flowchart LR\nA --> B', language: 'mermaid' }] },
        ],
      };
    }
    if (url.pathname === '/api/local/link') {
      const href = url.searchParams.get('href');
      if (href === 'choice') return { kind: 'choices', targets: ['GOAL-001', 'UC-001'], anchor: '' };
      if (href === 'missing') return { kind: 'unresolved', targets: [], message: 'Target is unavailable' };
      return { kind: 'document', targets: ['GOAL-001'], anchor: '' };
    }
    if (url.pathname === '/api/render') return { status: 400, body: { error: 'Renderer unavailable' } };
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open review' }).click();
  await page.getByRole('button', { name: 'Use Cases' }).click();
  await page.locator('.document-item', { hasText: 'UC-001' }).click();
  await expect(page.locator('.document-body')).toContainText('spec/sources/chat.md#Initial request');
  await expect(page.locator('.document-body ul li')).toHaveCount(3);
  await expect(page.locator('.diagram pre')).toContainText('flowchart LR');
  await expect(page.locator('.diagram-error')).toContainText('Renderer unavailable');
  await page.locator('.document-body a', { hasText: 'missing' }).click();
  await expect(page.getByRole('alert')).toContainText('Target is unavailable');
  await page.getByRole('button', { name: 'Dismiss' }).click();
  await page.locator('.document-body a', { hasText: 'choice' }).click();
  await expect(page.locator('.link-dialog', { hasText: 'Choose a linked artifact' })).toBeVisible();
  await page.locator('.link-dialog', { hasText: 'Choose a linked artifact' }).getByRole('button', { name: /GOAL-001/ }).click();
  await expect(page.locator('.doc-heading')).toContainText('GOAL-001');
});

test('keyboard opens review and navigates a named link dialog with focus return', async ({ page }) => {
  const selectedRevisions = [];
  await mockApi(page, (url) => {
    if (url.pathname === '/api/status') return { repo: '/tmp/sample', spec_dir: 'spec' };
    if (url.pathname === '/api/local/commits') return { branches: [], commits: [{ sha: 'base', subject: 'Base' }] };
    if (url.pathname === '/api/local/snapshot') {
      selectedRevisions.push(url.searchParams.get('ref'));
      return snapshot(url.searchParams.get('ref') || 'working tree');
    }
    if (url.pathname === '/api/local/document') return {
      document: url.searchParams.get('id') === 'GOAL-001' ? newGoal : useCase,
      revision: 'working tree',
      sections: [section('Description', 'See [choice](choice).')],
    };
    if (url.pathname === '/api/local/link') return { kind: 'choices', targets: ['GOAL-001', 'UC-001'], anchor: '' };
  });
  await page.goto('/');
  await tabTo(page, page.getByRole('button', { name: /Local folder/ }));
  await expect(page.getByRole('button', { name: /Local folder/ })).toBeFocused();
  const outline = await page.evaluate(() => getComputedStyle(document.activeElement).outlineStyle);
  expect(outline).not.toBe('none');
  await page.keyboard.press('Enter');
  await tabTo(page, page.getByRole('button', { name: 'Open review' }));
  await page.keyboard.press('Enter');
  await expect(page.getByRole('combobox', { name: 'Target revision' })).toBeVisible();
  await tabTo(page, page.getByRole('combobox', { name: 'Target revision' }));
  await expect(page.getByRole('combobox', { name: 'Target revision' })).toBeFocused();
  await page.keyboard.press('ArrowDown');
  await expect.poll(() => selectedRevisions.at(-1)).toBe('base');
  await tabTo(page, page.getByRole('button', { name: 'Use Cases' }));
  await expect(page.getByRole('button', { name: 'Use Cases' })).toBeFocused();
  await page.keyboard.press('Enter');
  await tabTo(page, page.locator('.document-item', { hasText: 'UC-001' }));
  await expect(page.locator('.document-item', { hasText: 'UC-001' })).toBeFocused();
  await page.keyboard.press('Enter');
  const link = page.getByRole('link', { name: 'choice' });
  await expect(link).toBeVisible();
  await tabTo(page, link);
  await expect(link).toBeFocused();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog', { name: 'Choose a linked artifact' });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole('button', { name: /GOAL-001/ })).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
  await expect(link).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(dialog).toBeVisible();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'GOAL-001 · Plan' })).toBeFocused();
});

test('a pending local comparison leaves filtering and overview navigation available', async ({ page }) => {
  let releaseComparison;
  const pending = new Promise((resolve) => { releaseComparison = resolve; });
  let comparisonFinished;
  const fulfilled = new Promise((resolve) => { comparisonFinished = resolve; });
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    let body;
    if (url.pathname === '/api/status') body = { repo: '/tmp/sample', spec_dir: 'spec' };
    else if (url.pathname === '/api/local/commits') body = { branches: [], commits: [{ sha: 'base', subject: 'Base' }] };
    else if (url.pathname === '/api/local/snapshot') body = snapshot('working tree');
    else if (url.pathname === '/api/local/compare') { await pending; body = comparison(); }
    else throw new Error(`Unexpected API request: ${url}`);
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(body) });
    if (url.pathname === '/api/local/compare') comparisonFinished();
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open review' }).click();
  await page.getByRole('button', { name: 'Compare', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('Loading revision');
  await page.getByRole('button', { name: 'Use Cases' }).click();
  await page.getByRole('textbox', { name: 'Filter documents' }).fill('UC-001');
  await expect(page.locator('.document-list')).toContainText('UC-001');
  await page.getByRole('button', { name: /Overview/ }).click();
  await expect(page.getByRole('button', { name: 'Open review' })).toBeVisible();
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.locator('.document-list')).toContainText('UC-001');
  releaseComparison();
  await fulfilled;
  await expect(page.locator('.revision-summary')).toHaveCount(0);
  await expect(page.getByRole('alert')).toHaveCount(0);
});
