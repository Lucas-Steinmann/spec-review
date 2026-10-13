// Deterministic data for previews and layout tests of the real Svelte dialogs.
export async function installDialogFixture(page, theme = 'paper') {
  await page.addInitScript((theme) => {
    localStorage.setItem('spec-review-theme', theme);
    localStorage.removeItem('spec-review-repositories');
  }, theme);
  await page.route('**/api/**', async (route) => {
    const url = new URL(route.request().url());
    let body;
    if (url.pathname === '/api/status') body = { repo: null, spec_dir: 'spec' };
    else if (url.pathname === '/api/local/folders') body = {
      path: url.searchParams.get('path') || '/home/reviewer', parent: '/home',
      folders: ['.config', '.copilot', '.devin', '.dotfiles', 'projects', 'worktrees', 'a-folder-with-a-long-name-that-must-fit-on-a-narrow-screen'].map((name) => ({ name, path: `/home/reviewer/${name}` })),
    };
    else if (url.pathname === '/api/gh/account') body = { login: 'reviewer' };
    else if (url.pathname === '/api/gh/repos') body = [{ full_name: 'optograph/companion-app', default_branch: 'main' }];
    else throw new Error(`Unexpected dialog preview request: ${url}`);
    await route.fulfill({ contentType: 'application/json', body: JSON.stringify(body) });
  });
}
