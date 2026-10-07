<script>
  import { onMount, tick } from 'svelte';
  import DocumentBody from './DocumentBody.svelte';

  let source = 'local';
  let status = null;
  let installations = [];
  let installation = '';
  let repos = [];
  let repo = '';
  let repoDefaults = {};
  let defaultBranch = '';
  let revisions = [];
  let revision = '';
  let base = '';
  let snapshot = null;
  let comparison = null;
  let categories = {};
  let category = 'goal';
  let search = '';
  let changesOnly = false;
  let selectedId = '';
  let currentDocument = null;
  let compareDocuments = null;
  let linkedDocument = null;
  let context = { source: 'local', ref: '' };
  let history = [];
  let error = '';
  let busy = false;
  let linkDialog;
  let linkChoices = [];
  let linkAnchor = '';
  let pendingLinkContext = null;
  let pendingLinkId = '';
  let page = 'overview';
  let savedRepos = JSON.parse(localStorage.getItem('spec-review-repositories') || '[]');
  let overviewRepo = '';
  let overviewPulls = [];
  let repoDialog;
  let addInstallation = '';
  let availableRepos = [];
  let addRepo = '';

  async function api(path, options = {}) {
    const response = await fetch(path, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || response.statusText);
    return result;
  }

  function queryFor(ctx, extra = {}) {
    const params = new URLSearchParams(extra);
    params.set('ref', ctx.ref || '');
    if (ctx.source === 'github') {
      params.set('installation', ctx.installation);
      const [owner, name] = ctx.repo.split('/');
      params.set('owner', owner);
      params.set('repo', name);
    }
    return params.toString();
  }

  function routeFor(ctx, action) {
    return `/api/${ctx.source}/${action}?${queryFor(ctx)}`;
  }

  function currentContext() {
    if (source === 'github') return { source, installation, repo, ref: revision };
    return { source, ref: revision };
  }

  function clearView() {
    currentDocument = null;
    compareDocuments = null;
    linkedDocument = null;
    selectedId = '';
  }

  async function initialize() {
    try {
      status = await api('/api/status');
      installations = await api('/api/github/installations').catch(() => []);
      addInstallation = String(installations[0]?.id || '');
      await refreshOverview();
    } catch (problem) { showError(problem); }
  }

  function repoQuery(item) {
    const [owner, name] = item.full_name.split('/');
    return new URLSearchParams({ installation: item.installation, owner, repo: name }).toString();
  }

  async function refreshOverview() {
    localStorage.setItem('spec-review-repositories', JSON.stringify(savedRepos));
    if (!savedRepos.some((item) => item.full_name === overviewRepo)) overviewRepo = savedRepos[0]?.full_name || '';
    if (!overviewRepo) { overviewPulls = []; return; }
    const item = savedRepos.find((row) => row.full_name === overviewRepo);
    try { overviewPulls = await api(`/api/github/overview?${repoQuery(item)}`); }
    catch (problem) { overviewPulls = []; showError(problem); }
  }

  async function openAddRepo() {
    try {
      installations = await api('/api/github/installations');
      addInstallation = String(installations[0]?.id || '');
      if (addInstallation) await loadAvailableRepos();
      repoDialog?.showModal();
    } catch (problem) { showError(problem); }
  }

  async function loadAvailableRepos() {
    availableRepos = await api(`/api/github/repos?installation=${encodeURIComponent(addInstallation)}`);
    addRepo = availableRepos.find((row) => !savedRepos.some((saved) => saved.full_name === row.full_name))?.full_name || '';
  }

  async function addRepository() {
    const item = availableRepos.find((row) => row.full_name === addRepo);
    if (!item) return;
    savedRepos = [...savedRepos.filter((row) => row.full_name !== item.full_name), { ...item, installation: addInstallation }];
    overviewRepo = item.full_name;
    repoDialog?.close();
    await refreshOverview();
  }

  async function openRepository(item) {
    page = 'detail';
    source = 'github'; installation = item.installation; repo = item.full_name;
    repoDefaults = { ...repoDefaults, [repo]: item.default_branch };
    repos = [...repos.filter((row) => row.full_name !== item.full_name), item];
    await loadGithubRevisions();
    await loadSnapshot();
  }

  async function openLocalRepository() {
    page = 'detail'; source = 'local';
    await loadLocalRevisions();
    await loadSnapshot();
  }

  async function openPull(pull) {
    const item = savedRepos.find((row) => row.full_name === overviewRepo);
    await openRepository(item);
    base = pull.base; revision = pull.head;
    await compareRevisions();
  }

  async function loadLocalRevisions() {
    const data = await api('/api/local/commits');
    revisions = [
      { label: 'Working tree', value: '' },
      ...data.branches.map((name) => ({ label: `Branch · ${name}`, value: name })),
      ...data.commits.map((item) => ({ label: `Commit · ${item.sha.slice(0, 10)} · ${item.subject}`, value: item.sha })),
    ];
    base = data.commits[1]?.sha || data.commits[0]?.sha || '';
    revision = '';
  }

  async function connectGithub() {
    installations = await api('/api/github/installations');
    installation = String(installations[0]?.id || '');
    if (!installation) throw new Error('No GitHub App installations are available.');
    await loadRepos();
  }

  async function loadRepos() {
    repos = await api(`/api/github/repos?installation=${encodeURIComponent(installation)}`);
    repoDefaults = Object.fromEntries(repos.map((item) => [item.full_name, item.default_branch]));
    repo = repos[0]?.full_name || '';
    if (!repo) throw new Error('This installation has no accessible repositories.');
    await loadGithubRevisions();
  }

  async function loadGithubRevisions() {
    defaultBranch = repoDefaults[repo] || 'main';
    const ctx = { source: 'github', installation, repo, ref: defaultBranch };
    const query = queryFor(ctx);
    const [branches, pulls, commits] = await Promise.all([
      api(`/api/github/branches?${query}`),
      api(`/api/github/pulls?${query}`),
      api(`/api/github/commits?${query}`),
    ]);
    revisions = [
      ...branches.map((item) => ({ label: `Branch · ${item.name}`, value: item.sha, branch: item.name })),
      ...pulls.map((item) => ({ label: `PR #${item.number} · ${item.title}`, value: item.head, base: item.base, pull: true })),
      ...commits.map((item) => ({ label: `Commit · ${item.sha.slice(0, 10)} · ${item.subject}`, value: item.sha, commit: true })),
    ];
    revisions.sort((left, right) => Number(right.branch === defaultBranch) - Number(left.branch === defaultBranch));
    revision = revisions.find((item) => item.branch === defaultBranch)?.value || revisions[0]?.value || '';
    base = commits[1]?.sha || commits[0]?.sha || '';
  }

  async function loadSnapshot() {
    busy = true;
    error = '';
    clearView();
    try {
      context = currentContext();
      snapshot = await api(routeFor(context, 'snapshot'));
      comparison = null;
      categories = snapshot.categories || {};
      if (!categories[category]) category = Object.keys(categories)[0] || '';
    } catch (problem) { showError(problem); }
    finally { busy = false; }
  }

  async function changeSource() {
    error = '';
    clearView();
    try {
      if (source === 'github') await connectGithub();
      else await loadLocalRevisions();
      await loadSnapshot();
    } catch (problem) { showError(problem); }
  }

  async function compareRevisions() {
    busy = true;
    error = '';
    clearView();
    try {
      const params = new URLSearchParams({ base, target: revision });
      if (source === 'github') {
        params.set('installation', installation);
        const [owner, name] = repo.split('/');
        params.set('owner', owner); params.set('repo', name);
      }
      comparison = await api(`/api/${source}/compare?${params}`);
      snapshot = comparison.target;
      categories = { ...comparison.base.categories, ...comparison.target.categories };
      if (!categories[category]) category = Object.keys(categories)[0] || '';
      context = currentContext();
    } catch (problem) { showError(problem); }
    finally { busy = false; }
  }

  function changedCategories() {
    if (!comparison) return new Set();
    const changed = new Set();
    for (const item of Object.values(comparison.changes)) {
      if (item.status === 'unchanged') continue;
      if (item.old) changed.add(item.old.type);
      if (item.new) changed.add(item.new.type);
    }
    return changed;
  }

  function entries() {
    let rows = comparison
      ? Object.values(comparison.changes).map((change) => ({ document: change.new || change.old, status: change.status }))
      : Object.values(snapshot?.documents || {}).map((document) => ({ document, status: 'unchanged' }));
    return rows.filter(({ document, status }) => document.type === category
      && (!changesOnly || status !== 'unchanged')
      && `${document.id} ${document.title}`.toLowerCase().includes(search.toLowerCase()))
      .sort((left, right) => left.document.id.localeCompare(right.document.id));
  }

  async function fetchDocument(id, ctx) {
    return api(`${routeFor(ctx, 'document')}&id=${encodeURIComponent(id)}`);
  }

  async function selectDocument(id) {
    selectedId = id;
    linkedDocument = null;
    currentDocument = null;
    compareDocuments = null;
    error = '';
    try {
      if (!comparison) currentDocument = await fetchDocument(id, context);
      else {
        const change = comparison.changes[id];
        const baseContext = { ...context, ref: comparison.base.revision };
        const targetContext = { ...context, ref: comparison.target.revision };
        const [oldDocument, newDocument] = await Promise.all([
          change.old ? fetchDocument(id, baseContext) : null,
          change.new ? fetchDocument(id, targetContext) : null,
        ]);
        compareDocuments = { base: oldDocument, target: newDocument, baseContext, targetContext, status: change.status };
      }
    } catch (problem) { showError(problem); }
  }

  function saveHistory() {
    history = [...history, {
      comparison, snapshot, categories, category, context, selectedId,
      currentDocument, compareDocuments, linkedDocument,
    }];
  }

  async function followLink(ctx, documentId, href) {
    try {
      const params = new URLSearchParams({ ...ctx, id: documentId, href });
      const result = await api(`/api/${ctx.source}/link?${params}`);
      if (result.kind === 'external') {
        window.open(result.url, '_blank', 'noopener,noreferrer');
      } else if (result.kind === 'unresolved') {
        error = result.message;
      } else if (result.kind === 'choices') {
        pendingLinkContext = ctx; pendingLinkId = result.targets[0];
        linkChoices = result.targets.map((id) => snapshotFor(ctx)?.documents?.[id] || { id, title: id });
        linkAnchor = result.anchor || '';
        linkDialog?.showModal();
      } else {
        await navigateLink(result.targets[0], ctx, result.anchor);
      }
    } catch (problem) { showError(problem); }
  }

  function snapshotFor(ctx) {
    if (!comparison) return snapshot;
    if (ctx.ref === comparison.base.revision) return comparison.base;
    if (ctx.ref === comparison.target.revision) return comparison.target;
    return snapshot;
  }

  async function navigateLink(id, ctx, anchor = '') {
    saveHistory();
    comparison = null;
    currentDocument = null; compareDocuments = null;
    selectedId = id;
    context = ctx;
    try {
      linkedDocument = await fetchDocument(id, ctx);
      if (anchor) {
        await tick();
        document.getElementById(anchor)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (problem) { showError(problem); }
  }

  async function chooseLink(id) {
    linkDialog?.close();
    await navigateLink(id, pendingLinkContext, linkAnchor);
  }

  function goBack() {
    const previous = history.at(-1);
    if (!previous) return;
    history = history.slice(0, -1);
    ({ comparison, snapshot, categories, category, context, selectedId, currentDocument, compareDocuments, linkedDocument } = previous);
  }

  async function revisionChanged() {
    const selected = revisions.find((item) => item.value === revision);
    if (selected?.base) base = selected.base;
    await loadSnapshot();
  }

  async function repoChanged() {
    await loadGithubRevisions();
    await loadSnapshot();
  }

  function showError(problem) { error = problem?.message || String(problem); }

  onMount(initialize);
</script>

<svelte:head><title>spec-review</title></svelte:head>

<header class="topbar">
  <a class="brand" href="/">spec-review</a>
  {#if page === 'detail'}
  <button on:click={() => { page = 'overview'; refreshOverview(); }}>← Overview</button>
  <div class="local-path">{repo || status?.repo || ''} <span>{status?.spec_dir || ''}</span></div>
  <label class="sr-only" for="source">Review source</label>
  <select id="source" bind:value={source} on:change={changeSource}>
    <option value="local">Local folder</option><option value="github">GitHub</option>
  </select>
  {#if source === 'github'}
    <select aria-label="GitHub account" bind:value={installation} on:change={loadRepos}>
      {#each installations as item}<option value={item.id}>{item.account} ({item.type})</option>{/each}
    </select>
    <select aria-label="GitHub repository" bind:value={repo} on:change={repoChanged}>
      {#each repos as item}<option value={item.full_name}>{item.full_name} · {item.default_branch}</option>{/each}
    </select>
  {/if}
  {:else}
  <span class="overview-title">Projects and pull requests</span><span class="spacer"></span>
  <button class="primary" on:click={openAddRepo}>Add</button>
  {/if}
</header>
{#if error}<div class="error-banner" role="alert">{error}<button aria-label="Dismiss" on:click={() => error = ''}>×</button></div>{/if}

{#if page === 'overview'}
<main class="overview-layout">
  <aside class="repo-sidebar"><h2>Repositories</h2>
    <button class:active={overviewRepo === '__local__'} on:click={() => { overviewRepo = '__local__'; overviewPulls = []; }}>Local folder · {status?.repo || ''}</button>
    {#if !savedRepos.length}<p class="empty">Add a GitHub repository to get started.</p>{/if}
    {#each savedRepos as item (item.full_name)}
      <button class:active={overviewRepo === item.full_name} on:click={() => { overviewRepo = item.full_name; refreshOverview(); }}>{item.full_name}</button>
    {/each}
  </aside>
  <section class="overview-content">
    {#if overviewRepo === '__local__'}
      <div class="overview-heading"><div><p>Local repository</p><h1>{status?.repo || 'Local folder'}</h1></div><button class="primary" on:click={openLocalRepository}>Open review</button></div>
      <p>Review the local specification and compare its revisions.</p>
    {:else if overviewRepo}
      <div class="overview-heading"><div><p>Repository</p><h1>{overviewRepo}</h1></div><button class="primary" on:click={() => openRepository(savedRepos.find((item) => item.full_name === overviewRepo))}>Open review</button></div>
      <h2>Open pull requests</h2>
      {#if overviewPulls.length}
        <div class="pull-list">{#each overviewPulls as pull (pull.number)}
          <button class="pull-card" on:click={() => openPull(pull)}><span class="pull-number">#{pull.number}</span><span class="pull-title"><strong>{pull.title}</strong><small>{pull.head_ref} → {pull.base_ref}</small></span><span class="checks {pull.checks}">{pull.checks === 'unavailable' ? 'Actions unavailable' : pull.checks.replace('_', ' ')}</span></button>
        {/each}</div>
      {:else}<p class="empty">No open pull requests.</p>{/if}
    {:else}<div class="empty-state">Add a GitHub repository to see its open pull requests.</div>{/if}
  </section>
</main>
<dialog bind:this={repoDialog} class="link-dialog add-dialog"><h2>Add GitHub repository</h2>
  <label>Account<select bind:value={addInstallation} on:change={loadAvailableRepos}>{#each installations as item}<option value={item.id}>{item.account} ({item.type})</option>{/each}</select></label>
  <label>Repository<select bind:value={addRepo}>{#each availableRepos as item}<option value={item.full_name}>{item.full_name}</option>{/each}</select></label>
  <div class="dialog-actions"><button on:click={() => repoDialog?.close()}>Cancel</button><button class="primary" disabled={!addRepo} on:click={addRepository}>Add repository</button></div>
</dialog>
{:else}
<nav class="revision-bar">
  <label>Target
    <select aria-label="Target revision" bind:value={revision} on:change={revisionChanged}>
      {#each revisions as item}<option value={item.value}>{item.label}</option>{/each}
    </select>
  </label>
  <label>Base
    <select aria-label="Base revision" bind:value={base}>
      {#each revisions as item}<option value={item.value}>{item.label}</option>{/each}
    </select>
  </label>
  <button class="primary" on:click={compareRevisions} disabled={busy}>Compare</button>
  <button on:click={loadSnapshot} disabled={busy}>Review version</button>
  <span class="spacer"></span>
  {#if history.length}<button on:click={goBack}>← Back</button>{/if}
  {#if comparison}<span class="revision-summary">{comparison.base.revision.slice(0, 10)} → {comparison.target.revision.slice(0, 10)}</span>{/if}
</nav>

<main class="workspace">
  <aside class="sidebar">
    <div class="filters"><input bind:value={search} placeholder="Filter ID or title" aria-label="Filter documents" />
      {#if comparison}<label class="checkbox"><input type="checkbox" bind:checked={changesOnly} /> Changes only</label>{/if}
    </div>
    <div class="category-list">
      {#each Object.entries(categories) as [key, label]}
        <button class:active={category === key} on:click={() => category = key}>{label}{#if changedCategories().has(key)} ★{/if}</button>
      {/each}
    </div>
    <div class="document-list">
      {#if busy}<p class="empty">Loading…</p>
      {:else if entries().length === 0}<p class="empty">No documents in this category.</p>
      {:else}
        {#each entries() as row (row.document.id)}
          <button class="document-item" class:active={selectedId === row.document.id} on:click={() => selectDocument(row.document.id)}>
            <span class={`change ${row.status}`}>{row.status === 'added' ? '+' : row.status === 'deleted' ? '−' : row.status === 'changed' ? '~' : ''}</span>
            <strong>{row.document.id}</strong><span>{row.document.title}</span>
          </button>
        {/each}
      {/if}
    </div>
    {#if snapshot?.diagnostics?.length}<div class="inventory">{snapshot.diagnostics.length} input diagnostics</div>{/if}
  </aside>

  <section class="content-pane">
    {#if linkedDocument}
      <div class="doc-heading"><div><h1>{linkedDocument.document.id} · {linkedDocument.document.title}</h1><p>{linkedDocument.revision} · {linkedDocument.document.path}</p></div></div>
      <DocumentBody sections={linkedDocument.sections} on:follow={(event) => followLink(context, linkedDocument.document.id, event.detail.href)} />
    {:else if compareDocuments}
      <div class="doc-heading"><div><h1>{selectedId} · {(compareDocuments.target || compareDocuments.base).document.title}</h1><p>{compareDocuments.status} · base {comparison.base.revision.slice(0, 10)} → target {comparison.target.revision.slice(0, 10)}</p></div></div>
      <div class="diff-columns">
        {#each [['Base', compareDocuments.base, compareDocuments.target, compareDocuments.baseContext], ['Target', compareDocuments.target, compareDocuments.base, compareDocuments.targetContext]] as [label, side, otherSide, sideContext]}
          <section class="diff-side"><h2>{label}{#if side}<small>{side.revision.slice(0, 10)}</small>{/if}</h2>
            {#if side}<DocumentBody sections={side.sections} diffAgainst={otherSide?.sections || []} on:follow={(event) => followLink(sideContext, side.document.id, event.detail.href)} />{:else}<p class="absent">Document absent in this revision.</p>{/if}
          </section>
        {/each}
      </div>
    {:else if currentDocument}
      <div class="doc-heading"><div><h1>{currentDocument.document.id} · {currentDocument.document.title}</h1><p>{currentDocument.revision} · {currentDocument.document.path}</p></div></div>
      <DocumentBody sections={currentDocument.sections} on:follow={(event) => followLink(context, currentDocument.document.id, event.detail.href)} />
    {:else}
      <div class="empty-state">{#if busy}Loading revision…{:else}Select a document to review.{/if}</div>
    {/if}
  </section>
</main>

<dialog bind:this={linkDialog} class="link-dialog">
  <h2>Choose a linked artifact</h2>
  {#each linkChoices as option}<button on:click={() => chooseLink(option.id)}><strong>{option.id}</strong><span>{option.title}</span></button>{/each}
  <button class="cancel" on:click={() => linkDialog?.close()}>Cancel</button>
</dialog>
{/if}
