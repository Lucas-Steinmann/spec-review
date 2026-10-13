import { expect, test } from '@playwright/test';

const local = { source: 'local', id: 'local-project', root: '/projects/sample', spec_dir: 'spec' };
const goal = { id: 'GOAL-001', type: 'goal', title: 'Shared goal', fields: {}, path: 'spec/artifacts/goals/GOAL-001.yaml' };
const snap = (ref) => ({ revision: ref || 'working tree', documents: { 'GOAL-001': goal }, categories: { goal: 'Goals' }, diagnostics: [] });
const metadata = {
  root: local.root, spec_dir: 'spec', is_git: true, default_base: 'main', branches: ['main', 'release'], commits: [{ sha: 'base-sha', subject: 'Base' }],
  worktrees: [
    { path: '/projects/sample', branch: 'main', head: 'base-sha', subject: 'Base', available: true },
    { path: '/projects/agent one', branch: 'agent-one', head: 'agent-sha', subject: 'Agent work', available: true },
    { path: '/projects/gone', branch: 'gone', head: 'gone-sha', subject: '', available: false },
  ],
};

async function mock(page, custom = () => undefined) {
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    let result = await custom(url);
    if (result === undefined) {
      if (url.pathname === '/api/status') result = { repo: null, spec_dir: 'spec' };
      else if (url.pathname === '/api/local/folders') {
        const path = url.searchParams.get('path') || '/home/user';
        result = { path, parent: '/', folders: [{ name: 'projects', path: '/projects' }, { name: 'sample', path: '/projects/sample' }] };
      } else if (url.pathname === '/api/local/validate') result = { ...metadata, root: url.searchParams.get('root'), spec_dir: url.searchParams.get('spec_dir') };
      else if (['/api/local/overview', '/api/local/commits'].includes(url.pathname)) result = metadata;
      else if (url.pathname === '/api/local/snapshot') result = snap(url.searchParams.get('ref'));
      else if (url.pathname === '/api/local/compare') result = { base: snap('base-sha'), target: snap(''), changes: { 'GOAL-001': { status: 'changed', old: goal, new: goal } } };
      else if (url.pathname === '/api/local/document') result = { document: goal, revision: url.searchParams.get('ref'), sections: [{ heading: 'Description', blocks: [{ kind: 'markdown', text: `Text from ${url.searchParams.get('worktree') || 'base'} [Goal](GOAL-001)` }] }] };
      else if (url.pathname === '/api/local/link') result = { kind: 'document', targets: ['GOAL-001'] };
      else throw new Error(`Unexpected request ${url}`);
    }
    await route.fulfill({ status: result.status || 200, contentType: 'application/json', body: JSON.stringify(result.body ?? result) });
  });
}

async function seed(page, sources = [local]) {
  await page.addInitScript((sources) => { if (!localStorage.getItem('spec-review-repositories')) localStorage.setItem('spec-review-repositories', JSON.stringify(sources)); }, sources);
}

test('empty startup and folder browser add multiple persistent sources without gh', async ({ page }) => {
  const requests = [];
  await mock(page, (url) => { requests.push(url.pathname); });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Add a workspace' })).toBeVisible();
  await expect(page.locator('.repo-entry')).toHaveCount(0);
  await page.getByRole('button', { name: 'Add repository', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Add repository', exact: true });
  await expect(dialog.getByRole('combobox', { name: 'Source type' })).toBeFocused();
  await expect(dialog.getByRole('textbox', { name: 'Folder path' })).toHaveValue('/home/user');
  await dialog.getByRole('button', { name: 'projects', exact: true }).click();
  await expect(dialog.getByRole('textbox', { name: 'Folder path' })).toHaveValue('/projects');
  await dialog.getByRole('button', { name: 'Parent folder' }).click();
  await expect(dialog.getByRole('textbox', { name: 'Folder path' })).toHaveValue('/');
  await dialog.getByRole('textbox', { name: 'Folder path' }).fill('/projects/sample');
  await dialog.getByRole('button', { name: 'Go', exact: true }).click();
  await expect(dialog.getByRole('textbox', { name: 'Folder path' })).toHaveValue('/projects/sample');
  await dialog.getByRole('button', { name: 'Add repository', exact: true }).click();
  await expect(page.locator('.repo-entry')).toHaveCount(1);
  await page.getByRole('button', { name: 'Add repository', exact: true }).click();
  await dialog.getByRole('textbox', { name: 'Folder path' }).fill('/projects/second');
  await dialog.getByRole('textbox', { name: 'Specification directory' }).fill('design/spec');
  await dialog.getByRole('button', { name: 'Add repository', exact: true }).click();
  await expect(page.locator('.repo-entry')).toHaveCount(2);
  await page.reload();
  await expect(page.locator('.repo-entry')).toHaveCount(2);
  await expect(page.locator('.repo-entry').last()).toContainText('design/spec');
  await page.getByRole('button', { name: 'Add repository', exact: true }).click();
  await dialog.getByRole('textbox', { name: 'Folder path' }).fill('/projects/second');
  await dialog.getByRole('textbox', { name: 'Specification directory' }).fill('design/spec');
  await dialog.getByRole('button', { name: 'Add repository', exact: true }).click();
  await expect(page.locator('.repo-entry')).toHaveCount(2);
  expect(requests.some((path) => path.startsWith('/api/gh/'))).toBe(false);
  await page.setViewportSize({ width: 430, height: 900 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth)).toBeLessThanOrEqual(1);
});

test('worktree cards use shared base and preserve both document and link contexts', async ({ page }) => {
  const requests = [];
  await seed(page);
  await mock(page, (url) => { requests.push(url); });
  await page.goto('/');
  await expect(page.getByRole('combobox', { name: 'Worktree base branch' })).toHaveValue('main');
  await expect(page.locator('.pull-card').last()).toBeDisabled();
  await page.getByRole('combobox', { name: 'Worktree base branch' }).selectOption('release');
  await page.reload();
  await expect(page.getByRole('combobox', { name: 'Worktree base branch' })).toHaveValue('release');
  await page.locator('.pull-card').filter({ hasText: 'agent-one' }).click();
  await expect(page.getByRole('combobox', { name: 'Review or compare' })).toHaveValue('compare');
  const compare = requests.findLast((url) => url.pathname === '/api/local/compare');
  expect(compare.searchParams.get('base')).toBe('release');
  expect(compare.searchParams.get('target')).toBe('');
  expect(compare.searchParams.get('target_worktree')).toBe('/projects/agent one');
  expect(compare.searchParams.get('root')).toBe(local.root);
  await page.getByRole('button', { name: /GOAL-001/ }).click();
  await expect(page.locator('.diff-side').last()).toContainText('Text from /projects/agent one');
  const docs = requests.filter((url) => url.pathname === '/api/local/document');
  expect(docs.at(-2).searchParams.get('worktree')).toBeNull();
  expect(docs.at(-2).searchParams.get('ref')).toBe('base-sha');
  expect(docs.at(-1).searchParams.get('worktree')).toBe('/projects/agent one');
  await page.locator('.diff-side').last().getByRole('link', { name: 'Goal', exact: true }).click();
  await expect(page.locator('.content-pane')).toContainText('Text from /projects/agent one');
  expect(requests.findLast((url) => url.pathname === '/api/local/link').searchParams.get('worktree')).toBe('/projects/agent one');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await expect(page.locator('.diff-side')).toHaveCount(2);
  await page.locator('.diff-side').first().getByRole('link', { name: 'Goal', exact: true }).click();
  await expect(page.locator('.content-pane')).toContainText('Text from base');
  expect(requests.findLast((url) => url.pathname === '/api/local/link').searchParams.get('worktree')).toBeNull();
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByRole('combobox', { name: 'Base revision' }).selectOption('worktree:/projects/agent one');
  await page.getByRole('combobox', { name: 'Target revision' }).selectOption('main');
  await page.getByRole('button', { name: 'Apply revision' }).click();
  const reverse = requests.findLast((url) => url.pathname === '/api/local/compare');
  expect(reverse.searchParams.get('base_worktree')).toBe('/projects/agent one');
  expect(reverse.searchParams.get('target_worktree')).toBeNull();
});

test('plain folders hide comparison and unavailable saved folders remain visible', async ({ page }) => {
  await seed(page, [local, { ...local, id: 'missing', root: '/missing' }]);
  await mock(page, (url) => {
    if (url.pathname === '/api/local/overview' && url.searchParams.get('root') === '/missing') return { status: 400, body: { error: 'Folder is unavailable' } };
    if (['/api/local/overview', '/api/local/commits'].includes(url.pathname)) return { ...metadata, is_git: false, branches: [], worktrees: [], default_base: '', commits: [] };
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.getByRole('combobox', { name: 'Review or compare' }).locator('option')).toHaveCount(1);
  await expect(page.getByRole('combobox', { name: 'Base revision' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Repositories', exact: true }).click();
  await page.locator('.repo-entry').last().click();
  await expect(page.getByRole('alert')).toContainText('Folder is unavailable');
  await expect(page.locator('.repo-entry')).toHaveCount(2);
  await expect(page.getByRole('button', { name: 'Open review' })).toBeDisabled();
});

test('old GitHub saved entries migrate and normal comparisons default to the default branch', async ({ page }) => {
  await seed(page, [{ full_name: 'owner/project', default_branch: 'main' }]);
  await mock(page, (url) => {
    if (['/api/gh/overview', '/api/gh/pulls'].includes(url.pathname)) return [];
    if (url.pathname === '/api/gh/branches') return [{ name: 'main', sha: 'main-sha' }, { name: 'feature', sha: 'feature-sha' }];
    if (url.pathname === '/api/gh/commits') return [{ sha: 'old-sha', subject: 'Old' }];
    if (url.pathname === '/api/gh/snapshot') return snap(url.searchParams.get('ref'));
  });
  await page.goto('/');
  await expect(page.locator('.repo-entry')).toContainText('owner/project');
  await page.getByRole('button', { name: 'Open review' }).click();
  await page.getByRole('combobox', { name: 'Review or compare' }).selectOption('compare');
  await expect(page.getByRole('combobox', { name: 'Base revision' })).toHaveValue('main-sha');
});

test('pending worktree comparisons cannot replace a newer source and Apply rereads files', async ({ page }) => {
  let release;
  const pending = new Promise((resolve) => { release = resolve; });
  let delayed = false;
  let compareCount = 0;
  await seed(page, [local, { ...local, id: 'second', root: '/projects/second' }]);
  await mock(page, async (url) => {
    if (url.pathname === '/api/local/compare') {
      compareCount += 1;
      if (!delayed) { delayed = true; await pending; }
      return { base: snap('base-sha'), target: snap(''), changes: { 'GOAL-001': { status: 'changed', old: goal, new: goal } } };
    }
  });
  await page.goto('/');
  await page.locator('.pull-card').filter({ hasText: 'agent-one' }).click();
  await expect(page.getByRole('status')).toContainText('Loading revision');
  await page.getByRole('button', { name: 'Repositories', exact: true }).click();
  await page.locator('.repo-entry').last().click();
  await page.getByRole('button', { name: 'Open review' }).click();
  await expect(page.locator('.local-path strong')).toHaveText('second');
  release();
  await expect(page.locator('.revision-summary')).toHaveCount(0);
  await page.getByRole('button', { name: /GOAL-001/ }).click();
  await expect(page.locator('.content-pane')).toContainText('Text from base');
  await page.getByRole('button', { name: 'Repositories', exact: true }).click();
  await page.locator('.repo-entry').first().click();
  await page.locator('.pull-card').filter({ hasText: 'agent-one' }).click();
  await expect(page.locator('.revision-summary')).toBeVisible();
  await page.getByRole('button', { name: 'Apply revision' }).click();
  await expect.poll(() => compareCount).toBe(3);
});
