<script>
  import { onMount, tick } from 'svelte';
  import { ArrowLeft, ArrowRight, ChevronRight, ExternalLink, Folder, GitBranch, Plus, Settings, X } from '@lucide/svelte';
  import DocumentBody from './DocumentBody.svelte';

  function readBooleanPreference(key, fallback) {
    const value = localStorage.getItem(key);
    return value === null ? fallback : value === 'true';
  }

  let status = null;
  let source = 'local';
  let repo = '';
  let defaultBranch = '';
  let ghAccount = '';
  let ghMessage = '';
  let savedRepos = JSON.parse(localStorage.getItem('spec-review-repositories') || '[]');
  let overviewRepo = '__local__';
  let overviewPulls = [];
  let overviewBusy = false;
  let overviewRequest = 0;
  let repoDialog;
  let availableRepos = [];
  let addRepo = '';
  let addBusy = false;
  let revisions = [];
  let revision = '';
  let reviewMode = ['review', 'compare'].includes(localStorage.getItem('spec-review-mode'))
    ? localStorage.getItem('spec-review-mode')
    : 'review';
  let base = '';
  let snapshot = null;
  let comparison = null;
  let categories = {};
  let category = 'goal';
  let search = '';
  let changesOnly = readBooleanPreference('spec-review-changes-only', false);
  let hideSuperseded = readBooleanPreference('spec-review-hide-superseded', true);
  let selectedId = '';
  let currentDocument = null;
  let compareDocuments = null;
  let linkedDocument = null;
  let context = { source: 'local', ref: '' };
  let history = [];
  let error = '';
  let busy = false;
  let viewRequest = 0;
  let linkDialog;
  let settingsDialog;
  let settingsButton;
  let linkChoices = [];
  let linkAnchor = '';
  let pendingLinkContext = null;
  let page = 'overview';
  let themeMode = ['system', 'dark', 'paper'].includes(localStorage.getItem('spec-review-theme'))
    ? localStorage.getItem('spec-review-theme')
    : 'system';
  let prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  $: resolvedTheme = themeMode === 'system' ? (prefersDark ? 'dark' : 'paper') : themeMode;
  $: {
    document.documentElement.dataset.theme = resolvedTheme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', resolvedTheme === 'dark' ? '#111613' : '#f4f4f0');
  }
  async function api(path, options = {}) {
    const response = await fetch(path, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || response.statusText);
    return result;
  }

  function queryFor(ctx, extra = {}) {
    const params = new URLSearchParams(extra);
    params.set('ref', ctx.ref || '');
    if (ctx.source === 'gh') {
      const [owner, name] = ctx.repo.split('/');
      params.set('owner', owner);
      params.set('repo', name);
    }
    return params.toString();
  }

  function routeFor(ctx, action) {
    return `/api/${ctx.source}/${action}?${queryFor(ctx)}`;
  }

  function currentContext() { return { source, repo, ref: revision }; }

  function clearView() {
    currentDocument = null;
    compareDocuments = null;
    linkedDocument = null;
    selectedId = '';
  }

  async function initialize() {
    try {
      status = await api('/api/status');
      if (savedRepos.length) {
        overviewRepo = savedRepos[0].full_name;
        refreshOverview();
      }
    }
    catch (problem) { showError(problem); }
  }

  async function openLocalRepository() {
    page = 'detail';
    source = 'local'; repo = '';
    try { await loadLocalRevisions(); await loadSnapshot(); }
    catch (problem) { showError(problem); }
  }

  function repoQuery(item) {
    const [owner, name] = item.full_name.split('/');
    return new URLSearchParams({ owner, repo: name }).toString();
  }

  async function refreshOverview() {
    const request = ++overviewRequest;
    overviewPulls = [];
    const item = savedRepos.find((row) => row.full_name === overviewRepo);
    if (!item) { overviewBusy = false; return; }
    overviewBusy = true;
    try {
      const pulls = await api(`/api/gh/overview?${repoQuery(item)}`);
      if (request === overviewRequest) overviewPulls = pulls;
    } catch (problem) { if (request === overviewRequest) showError(problem); }
    finally { if (request === overviewRequest) overviewBusy = false; }
  }

  async function openAddRepo() {
    addBusy = true;
    try {
      ghAccount = (await api('/api/gh/account')).login;
      availableRepos = await api('/api/gh/repos');
      addRepo = availableRepos.find((item) => !savedRepos.some((saved) => saved.full_name === item.full_name))?.full_name || '';
      repoDialog?.showModal();
      await tick();
      repoDialog?.querySelector('select')?.focus();
    } catch (problem) { ghMessage = problem.message; showError(problem); }
    finally { addBusy = false; }
  }

  async function addRepository() {
    const item = availableRepos.find((row) => row.full_name === addRepo);
    if (!item) return;
    savedRepos = [...savedRepos.filter((row) => row.full_name !== item.full_name), item];
    localStorage.setItem('spec-review-repositories', JSON.stringify(savedRepos));
    overviewRepo = item.full_name;
    repoDialog?.close();
    await refreshOverview();
  }

  async function openRepository(item, pull = null) {
    if (!item) return;
    const request = ++viewRequest;
    page = 'detail'; source = 'gh'; repo = item.full_name;
    defaultBranch = item.default_branch;
    busy = true;
    try {
      await loadGithubRevisions();
      if (request !== viewRequest || page !== 'detail') return;
      if (pull) {
        reviewMode = 'compare';
        base = pull.base; revision = pull.head;
        await compareRevisions();
      } else await loadSnapshot();
    } catch (problem) { if (request === viewRequest) showError(problem); }
    finally { if (request === viewRequest) busy = false; }
  }

  function openOverview() {
    viewRequest += 1;
    busy = false;
    page = 'overview';
    refreshOverview();
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

  async function loadGithubRevisions() {
    const ctx = { source: 'gh', repo, ref: defaultBranch };
    const query = queryFor(ctx);
    const [branches, pulls, commits] = await Promise.all([
      api(`/api/gh/branches?${query}`),
      api(`/api/gh/pulls?${query}`),
      api(`/api/gh/commits?${query}`),
    ]);
    revisions = [
      ...branches.map((item) => ({ label: `Branch · ${item.name}`, value: item.sha, branch: item.name })),
      ...pulls.map((item) => ({ label: `PR #${item.number} · ${item.title}`, value: item.head, base: item.base })),
      ...commits.map((item) => ({ label: `Commit · ${item.sha.slice(0, 10)} · ${item.subject}`, value: item.sha })),
    ];
    revisions.sort((left, right) => Number(right.branch === defaultBranch) - Number(left.branch === defaultBranch));
    revision = revisions.find((item) => item.branch === defaultBranch)?.value || revisions[0]?.value || '';
    base = commits[1]?.sha || commits[0]?.sha || '';
  }

  async function loadSnapshot() {
    const request = ++viewRequest;
    busy = true;
    error = '';
    clearView();
    try {
      context = currentContext();
      const loaded = await api(routeFor(context, 'snapshot'));
      if (request !== viewRequest || page !== 'detail') return;
      snapshot = loaded;
      comparison = null;
      categories = snapshot.categories || {};
      if (!categories[category]) category = Object.keys(categories)[0] || '';
    } catch (problem) { if (request === viewRequest) showError(problem); }
    finally { if (request === viewRequest) busy = false; }
  }

  async function compareRevisions() {
    const request = ++viewRequest;
    busy = true;
    error = '';
    try {
      const params = new URLSearchParams({ base, target: revision });
      if (source === 'gh') {
        const [owner, name] = repo.split('/');
        params.set('owner', owner); params.set('repo', name);
      }
      const loaded = await api(`/api/${source}/compare?${params}`);
      if (request !== viewRequest || page !== 'detail') return;
      comparison = loaded;
      clearView();
      snapshot = comparison.target;
      categories = { ...comparison.base.categories, ...comparison.target.categories };
      if (!categories[category]) category = Object.keys(categories)[0] || '';
      context = currentContext();
    } catch (problem) { if (request === viewRequest) showError(problem); }
    finally { if (request === viewRequest) busy = false; }
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

  function entries(sourceSnapshot, sourceComparison, selectedCategory, filterText, onlyChanges, hideSupersededItems) {
    let rows = sourceComparison
      ? Object.values(sourceComparison.changes).map((change) => ({ document: change.new || change.old, status: change.status }))
      : Object.values(sourceSnapshot?.documents || {}).map((document) => ({ document, status: 'unchanged' }));
    return rows.filter(({ document, status }) => document.type === selectedCategory
      && (!hideSupersededItems || document.fields?.status !== 'superseded')
      && (!onlyChanges || !sourceComparison || status !== 'unchanged')
      && `${document.id} ${document.title}`.toLowerCase().includes(filterText.toLowerCase()))
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
      const params = new URLSearchParams(queryFor(ctx));
      params.set('id', documentId);
      params.set('href', href);
      const result = await api(`/api/${ctx.source}/link?${params}`);
      if (result.kind === 'external') {
        window.open(result.url, '_blank', 'noopener,noreferrer');
      } else if (result.kind === 'unresolved') {
        error = result.message;
      } else if (result.kind === 'choices') {
        pendingLinkContext = ctx;
        linkChoices = result.targets.map((id) => snapshotFor(ctx)?.documents?.[id] || { id, title: id });
        linkAnchor = result.anchor || '';
        linkDialog?.showModal();
        await tick();
        linkDialog?.querySelector('button')?.focus();
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
      await tick();
      document.querySelector('.content-pane .doc-heading h1')?.focus();
      if (anchor) {
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
  }

  async function confirmSelection() {
    if (reviewMode === 'compare') await compareRevisions();
    else await loadSnapshot();
  }

  function showError(problem) { error = problem?.message || String(problem); }

  onMount(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const updatePreference = (event) => { prefersDark = event.matches; };
    media.addEventListener?.('change', updatePreference);
    initialize();
    return () => media.removeEventListener?.('change', updatePreference);
  });

  function setThemeMode(value) {
    themeMode = value;
    localStorage.setItem('spec-review-theme', value);
  }

  function localFolderName(path) {
    const normalized = (path || '').replace(/[\\/]+$/, '');
    return normalized.split(/[\\/]/).pop() || path || '';
  }

  function repositoryDisplayName() {
    return source === 'local' ? localFolderName(status?.repo) : repo || status?.repo || '';
  }

  async function openSettings() {
    settingsDialog?.showModal();
    await tick();
    settingsDialog?.querySelector('select')?.focus();
  }
</script>

<svelte:head><title>spec-review</title></svelte:head>

<header class="topbar">
  <a class="brand" href="/" aria-label="spec-review home"><span class="brand-mark" aria-hidden="true">s</span><span>spec<span class="brand-light">review</span></span></a>
  {#if page === 'detail'}
    <button class="quiet-button back-button" on:click={openOverview}><ArrowLeft size={15} aria-hidden="true" /> Repositories</button>
    <div class="local-path"><strong>{repositoryDisplayName()}</strong><span>{status?.spec_dir || ''}</span></div>
  {:else}
    <span class="topbar-context">Repository overview</span>
  {/if}
  <div class="topbar-actions">
    <button class="settings-button" bind:this={settingsButton} aria-label="Settings" title="Settings" on:click={openSettings}><Settings size={18} strokeWidth={1.8} aria-hidden="true" /></button>
    {#if page === 'overview'}<button class="primary" on:click={openAddRepo} disabled={addBusy}><Plus size={15} aria-hidden="true" /> Add repository</button>{/if}
  </div>
</header>
  {#if error}<div class="error-banner" role="alert">{error}<button aria-label="Dismiss" on:click={() => error = ''}><X size={16} aria-hidden="true" /></button></div>{/if}

{#if page === 'overview'}
<main class="overview-layout">
  <aside class="repo-sidebar"><div class="sidebar-heading"><span class="eyebrow">WORKSPACES</span><h2>Repositories</h2></div>
    <div class="repo-list"><button class="repo-entry" class:active={overviewRepo === '__local__'} on:click={() => { overviewRepo = '__local__'; refreshOverview(); }}><span class="repo-glyph local-glyph"><Folder size={15} aria-hidden="true" /></span><span class="repo-copy"><strong>Local folder</strong><small>{localFolderName(status?.repo) || 'This workspace'}</small></span><ChevronRight class="repo-chevron" size={16} aria-hidden="true" /></button>
    {#each savedRepos as item (item.full_name)}
      <button class="repo-entry" class:active={overviewRepo === item.full_name} on:click={() => { overviewRepo = item.full_name; refreshOverview(); }}><span class="repo-glyph"><GitBranch size={15} aria-hidden="true" /></span><span class="repo-copy"><strong>{item.full_name}</strong><small>GitHub repository</small></span><ChevronRight class="repo-chevron" size={16} aria-hidden="true" /></button>
    {/each}</div>
  </aside>
  <section class="overview-content">
    {#if addBusy}<p role="status">Loading GitHub repositories…</p>{/if}
    {#if overviewRepo === '__local__'}
      <div class="overview-heading"><div><p class="eyebrow">LOCAL WORKSPACE</p><h1>{localFolderName(status?.repo) || 'Local folder'}</h1><p class="overview-subtitle">Review the current specification or compare it with another revision.</p></div><button class="primary" on:click={openLocalRepository}>Open review <ExternalLink size={14} aria-hidden="true" /></button></div>
      <section class="overview-panel local-panel"><div class="panel-heading"><div><span class="eyebrow">LOCAL SOURCE</span><h2>Specification workspace</h2></div></div><p>Browse artifacts, follow references, and inspect changes across revisions from one focused workspace.</p></section>
    {:else}
      <div class="overview-heading"><div><p class="eyebrow">GITHUB WORKSPACE · {ghAccount || 'GH CLI'}</p><h1>{overviewRepo}</h1><p class="overview-subtitle">Choose a pull request to compare or open the repository’s current revision.</p></div><button class="primary" on:click={() => openRepository(savedRepos.find((item) => item.full_name === overviewRepo))}>Open review <ExternalLink size={14} aria-hidden="true" /></button></div>
      <div class="section-heading"><div><span class="eyebrow">REVIEW QUEUE</span><h2>Open pull requests</h2></div><span class="count-pill">{overviewPulls.length}</span></div>
      {#if overviewBusy}<p role="status">Loading pull requests…</p>
      {:else if overviewPulls.length}
        <div class="pull-list">{#each overviewPulls as pull (pull.number)}
          <button class="pull-card" on:click={() => openRepository(savedRepos.find((item) => item.full_name === overviewRepo), pull)}><span class="pull-number">#{pull.number}</span><span class="pull-title"><strong>{pull.title}</strong><small><code>{pull.head_ref}</code><ArrowRight size={12} aria-hidden="true" /><code>{pull.base_ref}</code></small></span><span class="checks {pull.checks}"><i></i>{pull.checks === 'unavailable' ? 'Actions unavailable' : pull.checks.replace('_', ' ')}</span><ExternalLink class="pull-open" size={14} aria-hidden="true" /></button>
        {/each}</div>
      {:else}<p class="empty">No open pull requests.</p>{/if}
    {/if}
    {#if ghMessage && !ghAccount}<p class="empty">Sign in with <code>gh auth login</code> to add GitHub repositories.</p>{/if}
  </section>
</main>
<dialog bind:this={repoDialog} class="link-dialog add-dialog" aria-labelledby="repo-dialog-title"><h2 id="repo-dialog-title">Add GitHub repository</h2>
  <label>Repository<select bind:value={addRepo}>{#each availableRepos as item}<option value={item.full_name}>{item.full_name}</option>{/each}</select></label>
  <div class="dialog-actions"><button on:click={() => repoDialog?.close()}>Cancel</button><button class="primary" disabled={!addRepo} on:click={addRepository}>Add repository</button></div>
</dialog>
{:else}
<nav class="revision-bar">
  <label><span>Mode</span>
    <select aria-label="Review or compare" bind:value={reviewMode} on:change={() => localStorage.setItem('spec-review-mode', reviewMode)}>
      <option value="review">Review</option>
      <option value="compare">Compare</option>
    </select>
  </label>
  <label><span>Target</span>
    <select aria-label="Target revision" bind:value={revision} on:change={revisionChanged}>
      {#each revisions as item}<option value={item.value}>{item.label}</option>{/each}
    </select>
  </label>
  {#if reviewMode === 'compare'}<label><span>Base</span>
    <select aria-label="Base revision" bind:value={base}>
      {#each revisions as item}<option value={item.value}>{item.label}</option>{/each}
    </select>
  </label>{/if}
  <button class="primary confirm-button" on:click={confirmSelection} disabled={busy}>{busy ? 'Loading…' : 'Apply revision'}</button>
  <span class="spacer"></span>
  {#if history.length}<button on:click={goBack}><ArrowLeft size={14} aria-hidden="true" /> Back</button>{/if}
  {#if comparison}<span class="revision-summary">{comparison.base.revision.slice(0, 10)} → {comparison.target.revision.slice(0, 10)}</span>{/if}
</nav>

<main class="workspace">
  <aside class="sidebar">
    <div class="filters"><input bind:value={search} placeholder="Filter ID or title" aria-label="Filter documents" />
      <label class="checkbox"><input type="checkbox" bind:checked={hideSuperseded} on:change={() => localStorage.setItem('spec-review-hide-superseded', String(hideSuperseded))} /> Hide superseded</label>
      {#if comparison}<label class="checkbox"><input type="checkbox" bind:checked={changesOnly} on:change={() => localStorage.setItem('spec-review-changes-only', String(changesOnly))} /> Changes only</label>{/if}
    </div>
    <div class="category-list">
      {#each Object.entries(categories) as [key, label]}
        <button class:active={category === key} on:click={() => category = key}>{label}{#if changedCategories().has(key)} ★{/if}</button>
      {/each}
    </div>
    <div class="document-list">
      {#if busy}<p class="loading-status" role="status">Loading revision…</p>{/if}
      {#if entries(snapshot, comparison, category, search, changesOnly, hideSuperseded).length === 0}<p class="empty">No documents in this category.</p>
      {:else}
        {#each entries(snapshot, comparison, category, search, changesOnly, hideSuperseded) as row (row.document.id)}
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
      <div class="doc-heading"><div><h1 tabindex="-1">{linkedDocument.document.id} · {linkedDocument.document.title}</h1><p>{linkedDocument.revision} · {linkedDocument.document.path}</p></div></div>
      <DocumentBody sections={linkedDocument.sections} on:follow={(event) => followLink(context, linkedDocument.document.id, event.detail.href)} />
    {:else if compareDocuments}
      <div class="doc-heading"><div><h1>{selectedId} · {(compareDocuments.target || compareDocuments.base).document.title}</h1><p>{compareDocuments.status} · base {comparison.base.revision.slice(0, 10)} → target {comparison.target.revision.slice(0, 10)}</p></div></div>
      <div class="diff-columns">
        {#each [['Base', compareDocuments.base, compareDocuments.target, compareDocuments.baseContext], ['Target', compareDocuments.target, compareDocuments.base, compareDocuments.targetContext]] as [label, side, otherSide, sideContext]}
          <section class="diff-side"><h2>{label}{#if side}<small>{side.revision.slice(0, 10)}</small>{/if}</h2>
            {#if side}<DocumentBody sections={side.sections} diffAgainst={otherSide?.sections || []} diffKind={label === 'Base' ? 'removed' : 'added'} on:follow={(event) => followLink(sideContext, side.document.id, event.detail.href)} />{:else}<p class="absent">Document absent in this revision.</p>{/if}
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

<dialog bind:this={linkDialog} class="link-dialog" aria-labelledby="link-dialog-title">
  <h2 id="link-dialog-title">Choose a linked artifact</h2>
  {#each linkChoices as option}<button on:click={() => chooseLink(option.id)}><strong>{option.id}</strong><span>{option.title}</span></button>{/each}
  <button class="cancel" on:click={() => linkDialog?.close()}>Cancel</button>
</dialog>
{/if}
<dialog bind:this={settingsDialog} class="link-dialog settings-dialog" aria-labelledby="settings-title" on:close={() => settingsButton?.focus()}>
  <div class="settings-heading"><div><span class="eyebrow">PREFERENCES</span><h2 id="settings-title">Settings</h2></div><button class="icon-close" aria-label="Close settings" on:click={() => settingsDialog?.close()}><X size={18} aria-hidden="true" /></button></div>
  <label class="setting-row"><span><strong>Appearance</strong><small>Choose how the workspace looks.</small></span><select aria-label="Appearance" value={themeMode} on:change={(event) => setThemeMode(event.currentTarget.value)}>
    <option value="system">System</option><option value="paper">Paper</option><option value="dark">Dark</option>
  </select></label>
  <div class="dialog-actions"><button class="primary" on:click={() => settingsDialog?.close()}>Done</button></div>
</dialog>
