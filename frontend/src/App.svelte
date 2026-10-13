<script>
  import { onMount, tick } from 'svelte';
  import { ArrowLeft, ArrowRight, ChevronRight, ExternalLink, Folder, GitBranch, Plus, Settings, X } from '@lucide/svelte';
  import Button from './ui/Button.svelte';
  import LinkChoiceDialog from './components/LinkChoiceDialog.svelte';
  import FormField from './ui/FormField.svelte';
  import AddRepositoryDialog from './components/AddRepositoryDialog.svelte';
  import SettingsDialog from './components/SettingsDialog.svelte';
  import DocumentBody from './DocumentBody.svelte';

  const categoryOrder = [
    'goal', 'actor', 'use_case', 'requirement', 'constraint', 'decision',
    'design', 'ui_design', 'test', 'risk', 'assumption', 'question', 'overview',
  ];

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
  function readSources() {
    try { return JSON.parse(localStorage.getItem('spec-review-repositories') || '[]').map((item) => item.source ? item : { ...item, source: 'gh', id: item.full_name }); }
    catch { return []; }
  }
  let savedRepos = readSources();
  let overviewRepo = '';
  let localOverview = null;
  let overviewBase = '';
  let specDir = 'spec';
  let isGit = true;
  let addSource = 'local';
  let folderListing = null;
  let folderPath = '';
  let addSpecDir = 'spec';
  let addError = '';
  let folderRequest = 0;
  let addRequest = 0;
  $: overviewItem = savedRepos.find((item) => item.id === overviewRepo);
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
  let documentRequest = 0;
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
    if (ctx.source === 'local') {
      params.set('root', ctx.repo || '');
      params.set('spec_dir', ctx.specDir || 'spec');
      if (ctx.worktree) params.set('worktree', ctx.worktree);
    }
    return params.toString();
  }

  function routeFor(ctx, action) {
    return `/api/${ctx.source}/${action}?${queryFor(ctx)}`;
  }

  function revisionContext(value) {
    return { source, repo, specDir, ref: value.startsWith('worktree:') ? '' : value,
      worktree: value.startsWith('worktree:') ? value.slice(9) : '' };
  }
  function currentContext() { return revisionContext(revision); }

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
        const selected = localStorage.getItem('spec-review-selected-source');
        overviewRepo = savedRepos.some((item) => item.id === selected) ? selected : savedRepos[0].id;
        refreshOverview();
      }
    }
    catch (problem) { showError(problem); }
  }

  async function openLocalRepository(item = overviewItem, worktree = null) {
    if (!item) return;
    overviewRequest += 1;
    const request = ++viewRequest;
    page = 'detail'; source = 'local'; repo = item.root; specDir = item.spec_dir;
    history = []; clearView(); busy = true;
    try {
      const data = await api(routeFor({ source, repo, specDir, ref: '' }, 'commits'));
      if (request !== viewRequest || page !== 'detail') return;
      isGit = Boolean(data.is_git && data.default_base);
      revisions = [
        { label: 'Working tree', value: '' },
        ...data.branches.map((name) => ({ label: `Branch · ${name}`, value: name })),
        ...(data.default_base === 'HEAD' ? [{ label: 'HEAD', value: 'HEAD' }] : []),
        ...data.commits.map((entry) => ({ label: `Commit · ${entry.sha.slice(0, 10)} · ${entry.subject}`, value: entry.sha })),
        ...(data.worktrees || []).filter((entry) => entry.available && !entry.bare).map((entry) => ({ label: `Worktree · ${entry.branch || 'Detached HEAD'} · ${localFolderName(entry.path)}`, value: `worktree:${entry.path}` })),
      ];
      base = overviewBase || data.default_base || '';
      revision = worktree ? `worktree:${worktree.path}` : '';
      if (worktree) { reviewMode = 'compare'; await compareRevisions(); }
      else { if (!isGit) reviewMode = 'review'; await loadSnapshot(); }
    } catch (problem) { if (request === viewRequest) showError(problem); }
    finally { if (request === viewRequest) busy = false; }
  }

  function repoQuery(item) {
    const [owner, name] = item.full_name.split('/');
    return new URLSearchParams({ owner, repo: name }).toString();
  }

  function persistSources() {
    localStorage.setItem('spec-review-repositories', JSON.stringify(savedRepos));
  }

  function changeOverviewBase() {
    savedRepos = savedRepos.map((item) => item.id === overviewRepo ? { ...item, base: overviewBase } : item);
    persistSources();
  }

  async function refreshOverview() {
    localStorage.setItem('spec-review-selected-source', overviewRepo);
    const request = ++overviewRequest;
    overviewPulls = []; localOverview = null; overviewBase = '';
    const item = savedRepos.find((row) => row.id === overviewRepo);
    if (!item) { overviewBusy = false; return; }
    overviewBusy = true; error = '';
    try {
      if (item.source === 'local') {
        const data = await api(routeFor({ source: 'local', repo: item.root, specDir: item.spec_dir, ref: '' }, 'overview'));
        if (request !== overviewRequest) return;
        localOverview = data;
        overviewBase = [...data.branches, 'HEAD'].includes(item.base) ? item.base : data.default_base;
      } else {
        const pulls = await api(`/api/gh/overview?${repoQuery(item)}`);
        if (request === overviewRequest) overviewPulls = pulls;
      }
    } catch (problem) { if (request === overviewRequest) showError(problem); }
    finally { if (request === overviewRequest) overviewBusy = false; }
  }

  async function browseFolders(path = '') {
    const request = ++folderRequest;
    addBusy = true; addError = '';
    try {
      const data = await api(`/api/local/folders?${new URLSearchParams(path ? { path } : {})}`);
      if (request !== folderRequest || addSource !== 'local') return;
      folderListing = data; folderPath = data.path;
    } catch (problem) { if (request === folderRequest && addSource === 'local') addError = problem.message; }
    finally { if (request === folderRequest && addSource === 'local') addBusy = false; }
  }

  async function loadAddSource() {
    const request = ++addRequest;
    addError = ''; folderRequest += 1;
    if (addSource === 'local') { await browseFolders(folderPath); return; }
    addBusy = true;
    try {
      const account = await api('/api/gh/account');
      if (request !== addRequest) return;
      ghAccount = account.login;
      const repos = await api('/api/gh/repos');
      if (request !== addRequest) return;
      availableRepos = repos;
      addRepo = availableRepos.find((item) => !savedRepos.some((saved) => saved.full_name === item.full_name))?.full_name || '';
    } catch (problem) { if (request === addRequest) { ghMessage = problem.message; addError = problem.message; } }
    finally { if (request === addRequest) addBusy = false; }
  }

  async function openAddRepo() {
    addSource = 'local'; addError = ''; addSpecDir = 'spec';
    repoDialog?.showModal();
    await tick();
    await loadAddSource();
  }

  function cancelAddRequests() {
    addRequest += 1;
    folderRequest += 1;
    addBusy = false;
  }

  async function addRepository() {
    const request = ++addRequest;
    addBusy = true; addError = '';
    try {
      let item;
      if (addSource === 'local') {
        const data = await api(`/api/local/validate?${new URLSearchParams({ root: folderPath, spec_dir: addSpecDir })}`);
        item = { source: 'local', root: data.root, spec_dir: data.spec_dir, id: `local:${JSON.stringify([data.root, data.spec_dir])}` };
      } else {
        const found = availableRepos.find((row) => row.full_name === addRepo);
        if (!found) return;
        item = { ...found, source: 'gh', id: found.full_name };
      }
      if (request !== addRequest || page !== 'overview') return;
      item = { ...savedRepos.find((row) => row.id === item.id), ...item };
      savedRepos = [...savedRepos.filter((row) => row.id !== item.id), item];
      persistSources(); overviewRepo = item.id;
      repoDialog?.close(); await refreshOverview();
    } catch (problem) { if (request === addRequest) addError = problem.message; }
    finally { if (request === addRequest) addBusy = false; }
  }

  async function openRepository(item, pull = null) {
    if (!item) return;
    overviewRequest += 1;
    const request = ++viewRequest;
    page = 'detail'; source = 'gh'; repo = item.full_name; specDir = 'spec'; isGit = true; history = []; clearView();
    defaultBranch = item.default_branch;
    busy = true;
    try {
      await loadGithubRevisions(request);
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

  async function loadGithubRevisions(request) {
    const ctx = { source: 'gh', repo, ref: defaultBranch };
    const query = queryFor(ctx);
    const [branches, pulls, commits] = await Promise.all([
      api(`/api/gh/branches?${query}`),
      api(`/api/gh/pulls?${query}`),
      api(`/api/gh/commits?${query}`),
    ]);
    if (request !== viewRequest || page !== 'detail') return;
    revisions = [
      ...branches.map((item) => ({ label: `Branch · ${item.name}`, value: item.sha, branch: item.name })),
      ...pulls.map((item) => ({ label: `PR #${item.number} · ${item.title}`, value: item.head, base: item.base })),
      ...commits.map((item) => ({ label: `Commit · ${item.sha.slice(0, 10)} · ${item.subject}`, value: item.sha })),
    ];
    revisions.sort((left, right) => Number(right.branch === defaultBranch) - Number(left.branch === defaultBranch));
    revision = revisions.find((item) => item.branch === defaultBranch)?.value || revisions[0]?.value || '';
    base = revisions.find((item) => item.branch === defaultBranch)?.value || revisions[0]?.value || '';
  }

  async function loadSnapshot() {
    const request = ++viewRequest;
    busy = true;
    error = '';
    clearView();
    try {
      const selectedContext = currentContext();
      const loaded = await api(routeFor(selectedContext, 'snapshot'));
      if (request !== viewRequest || page !== 'detail') return;
      context = { ...selectedContext, ref: loaded.revision };
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
      const baseContext = revisionContext(base);
      const targetContext = currentContext();
      const params = new URLSearchParams({ base: baseContext.ref, target: targetContext.ref });
      if (source === 'local') {
        params.set('root', repo); params.set('spec_dir', specDir);
        if (baseContext.worktree) params.set('base_worktree', baseContext.worktree);
        if (targetContext.worktree) params.set('target_worktree', targetContext.worktree);
      }
      if (source === 'gh') {
        const [owner, name] = repo.split('/');
        params.set('owner', owner); params.set('repo', name);
      }
      const loaded = await api(`/api/${source}/compare?${params}`);
      if (request !== viewRequest || page !== 'detail') return;
      comparison = { ...loaded, baseContext: { ...baseContext, ref: loaded.base.revision }, targetContext: { ...targetContext, ref: loaded.target.revision } };
      clearView();
      snapshot = comparison.target;
      categories = { ...comparison.base.categories, ...comparison.target.categories };
      if (!categories[category]) category = Object.keys(categories)[0] || '';
      context = comparison.targetContext;
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

  function orderedCategoryEntries() {
    return Object.entries(categories).sort(([left], [right]) => {
      const leftIndex = categoryOrder.indexOf(left);
      const rightIndex = categoryOrder.indexOf(right);
      return (leftIndex < 0 ? categoryOrder.length : leftIndex)
        - (rightIndex < 0 ? categoryOrder.length : rightIndex);
    });
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
    const request = ++documentRequest;
    const selectedView = viewRequest;
    selectedId = id;
    linkedDocument = null;
    currentDocument = null;
    compareDocuments = null;
    error = '';
    try {
      if (!comparison) {
        const loaded = await fetchDocument(id, context);
        if (request !== documentRequest || selectedView !== viewRequest || page !== 'detail') return;
        currentDocument = loaded;
      }
      else {
        const change = comparison.changes[id];
        const baseContext = comparison.baseContext;
        const targetContext = comparison.targetContext;
        const [oldDocument, newDocument] = await Promise.all([
          change.old ? fetchDocument(id, baseContext) : null,
          change.new ? fetchDocument(id, targetContext) : null,
        ]);
        if (request !== documentRequest || selectedView !== viewRequest || page !== 'detail') return;
        compareDocuments = { base: oldDocument, target: newDocument, baseContext, targetContext, status: change.status };
      }
    } catch (problem) { if (request === documentRequest && selectedView === viewRequest) showError(problem); }
  }

  function saveHistory() {
    history = [...history, {
      comparison, snapshot, categories, category, context, selectedId,
      currentDocument, compareDocuments, linkedDocument,
    }];
  }

  async function followLink(ctx, documentId, href) {
    const request = viewRequest;
    const selectedDocument = documentRequest;
    try {
      const params = new URLSearchParams(queryFor(ctx));
      params.set('id', documentId);
      params.set('href', href);
      const result = await api(`/api/${ctx.source}/link?${params}`);
      if (request !== viewRequest || selectedDocument !== documentRequest || page !== 'detail') return;
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

      } else {
        await navigateLink(result.targets[0], ctx, result.anchor);
      }
    } catch (problem) { if (request === viewRequest) showError(problem); }
  }

  function snapshotFor(ctx) {
    if (!comparison) return snapshot;
    if (ctx.ref === comparison.base.revision && ctx.worktree === comparison.baseContext.worktree) return comparison.base;
    if (ctx.ref === comparison.target.revision) return comparison.target;
    return snapshot;
  }

  async function navigateLink(id, ctx, anchor = '') {
    const request = ++viewRequest;
    busy = false;
    saveHistory();
    comparison = null;
    currentDocument = null; compareDocuments = null;
    selectedId = id;
    context = ctx;
    try {
      const loaded = await fetchDocument(id, ctx);
      if (request !== viewRequest || page !== 'detail') return;
      linkedDocument = loaded;
      await tick();
      document.querySelector('.content-pane .doc-heading h1')?.focus();
      if (anchor) {
        document.getElementById(anchor)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (problem) { if (request === viewRequest) showError(problem); }
  }

  async function chooseLink(id) {
    linkDialog?.close();
    await navigateLink(id, pendingLinkContext, linkAnchor);
  }

  function goBack() {
    viewRequest += 1;
    busy = false;
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
    return source === 'local' ? localFolderName(context.worktree || repo) : repo || '';
  }

  async function openSettings() {
    settingsDialog?.showModal();
    await tick();
  }
</script>

<svelte:head><title>spec-review</title></svelte:head>

<header class="topbar">
  <a class="brand" href="/" aria-label="spec-review home"><span class="brand-mark" aria-hidden="true">s</span><span>spec<span class="brand-light">review</span></span></a>
  {#if page === 'detail'}
    <Button variant="quiet" class="quiet-button back-button" on:click={openOverview}><ArrowLeft size={15} aria-hidden="true" /> Repositories</Button>
    <div class="local-path"><strong>{repositoryDisplayName()}</strong><span>{specDir}</span></div>
  {:else}
    <span class="topbar-context">Repository overview</span>
  {/if}
  <div class="topbar-actions">
    <Button variant="icon" class="settings-button" bind:element={settingsButton} aria-label="Settings" title="Settings" on:click={openSettings}><Settings size={18} strokeWidth={1.8} aria-hidden="true" /></Button>
    {#if page === 'overview'}<Button variant="primary" compact on:click={openAddRepo} disabled={addBusy}><Plus size={15} aria-hidden="true" /> Add repository</Button>{/if}
  </div>
</header>
  {#if error}<div class="error-banner" role="alert">{error}<Button variant="icon" compact aria-label="Dismiss" on:click={() => error = ''}><X size={16} aria-hidden="true" /></Button></div>{/if}

{#if page === 'overview'}
<main class="overview-layout">
  <aside class="repo-sidebar"><div class="sidebar-heading"><span class="eyebrow">WORKSPACES</span><h2>Repositories</h2></div>
    <div class="repo-list">
    {#each savedRepos as item (item.id)}
      <button class="repo-entry" class:active={overviewRepo === item.id} on:click={() => { overviewRepo = item.id; refreshOverview(); }}><span class="repo-glyph" class:local-glyph={item.source === 'local'}>{#if item.source === 'local'}<Folder size={15} aria-hidden="true" />{:else}<GitBranch size={15} aria-hidden="true" />{/if}</span><span class="repo-copy"><strong>{item.source === 'local' ? localFolderName(item.root) : item.full_name}</strong><small>{item.source === 'local' ? `Local folder · ${item.spec_dir}` : 'GitHub repository'}</small></span><ChevronRight class="repo-chevron" size={16} aria-hidden="true" /></button>
    {/each}</div>
  </aside>
  <section class="overview-content">
    {#if !overviewItem}
      <div class="overview-heading"><div><h1>Add a workspace</h1><p>Use Add repository to choose a local folder or GitHub repository.</p></div></div>
    {:else if overviewItem.source === 'local'}
      <div class="overview-heading"><div><p class="eyebrow">LOCAL WORKSPACE</p><h1>{localFolderName(overviewItem.root)}</h1><p class="overview-subtitle">Review the current specification or compare worktrees against a base branch.</p></div><Button variant="primary" disabled={!localOverview} on:click={() => openLocalRepository()}>Open review <ExternalLink size={14} aria-hidden="true" /></Button></div>
      <section class="overview-panel local-panel"><div class="panel-heading"><div><span class="eyebrow">LOCAL SOURCE</span><h2>Specification workspace</h2></div><Button variant="secondary" disabled={overviewBusy} on:click={refreshOverview}>Refresh</Button></div><p>{overviewItem.root} · {overviewItem.spec_dir}</p></section>
      {#if overviewBusy}<p role="status">Loading worktrees…</p>{/if}
      {#if localOverview?.is_git}
        <div class="section-heading"><div><span class="eyebrow">REVIEW QUEUE</span><h2>Worktrees</h2></div><FormField label="Base branch" class="overview-base"><select class="ui-control" aria-label="Worktree base branch" bind:value={overviewBase} on:change={changeOverviewBase}>{#each localOverview.branches as branch}<option value={branch}>{branch}</option>{/each}{#if localOverview.default_base === 'HEAD'}<option value="HEAD">HEAD</option>{/if}</select></FormField></div>
        <div class="pull-list">{#each localOverview.worktrees.filter((entry) => !entry.bare) as worktree (worktree.path)}
          <button class="pull-card" disabled={!worktree.available || !overviewBase} on:click={() => openLocalRepository(overviewItem, worktree)}><GitBranch size={18} aria-hidden="true" /><span class="pull-title"><strong>{worktree.branch || 'Detached HEAD'}</strong><small>{worktree.path}</small><small>{worktree.head.slice(0, 10)} · {worktree.subject}</small></span><span>{worktree.available ? `Compare with ${overviewBase}` : 'Unavailable'}</span><ExternalLink size={14} aria-hidden="true" /></button>
        {/each}</div>
      {:else if localOverview}<p class="empty">This folder has no Git history. Open review to browse its current files.</p>{/if}
    {:else}
      <div class="overview-heading"><div><p class="eyebrow">GITHUB WORKSPACE · {ghAccount || 'GH CLI'}</p><h1>{overviewItem.full_name}</h1><p class="overview-subtitle">Choose a pull request to compare or open the repository’s current revision.</p></div><Button variant="primary" on:click={() => openRepository(overviewItem)}>Open review <ExternalLink size={14} aria-hidden="true" /></Button></div>
      <div class="section-heading"><div><span class="eyebrow">REVIEW QUEUE</span><h2>Open pull requests</h2></div><span class="count-pill">{overviewPulls.length}</span></div>
      {#if overviewBusy}<p role="status">Loading pull requests…</p>
      {:else if overviewPulls.length}
        <div class="pull-list">{#each overviewPulls as pull (pull.number)}
          <button class="pull-card" on:click={() => openRepository(overviewItem, pull)}><span class="pull-number">#{pull.number}</span><span class="pull-title"><strong>{pull.title}</strong><small><code>{pull.head_ref}</code><ArrowRight size={12} aria-hidden="true" /><code>{pull.base_ref}</code></small></span><span class="checks {pull.checks}"><i></i>{pull.checks === 'unavailable' ? 'Actions unavailable' : pull.checks.replace('_', ' ')}</span><ExternalLink class="pull-open" size={14} aria-hidden="true" /></button>
        {/each}</div>
      {:else}<p class="empty">No open pull requests.</p>{/if}
    {/if}
    {#if ghMessage && !ghAccount}<p class="empty">Sign in with <code>gh auth login</code> to add GitHub repositories.</p>{/if}
  </section>
</main>
<AddRepositoryDialog bind:this={repoDialog} bind:source={addSource} bind:path={folderPath} bind:specDir={addSpecDir} bind:repository={addRepo} listing={folderListing} repositories={availableRepos} busy={addBusy} error={addError} on:sourcechange={loadAddSource} on:browse={(event) => browseFolders(event.detail)} on:add={addRepository} on:close={cancelAddRequests} />
{:else}
<nav class="revision-bar">
  <FormField label="Mode" compact class="revision-field">
    <select class="ui-control" aria-label="Review or compare" bind:value={reviewMode} on:change={() => localStorage.setItem('spec-review-mode', reviewMode)}>
      <option value="review">Review</option>
      {#if isGit}<option value="compare">Compare</option>{/if}
    </select>
  </FormField>
  <FormField label="Target" compact class="revision-field">
    <select class="ui-control" aria-label="Target revision" bind:value={revision} on:change={revisionChanged}>
      {#each revisions as item}<option value={item.value}>{item.label}</option>{/each}
    </select>
  </FormField>
  {#if reviewMode === 'compare'}<FormField label="Base" compact class="revision-field">
    <select class="ui-control" aria-label="Base revision" bind:value={base}>
      {#each revisions as item}<option value={item.value}>{item.label}</option>{/each}
    </select>
  </FormField>{/if}
  <Button variant="primary" class="confirm-button" on:click={confirmSelection} disabled={busy}>{busy ? 'Loading…' : 'Apply revision'}</Button>
  <span class="spacer"></span>
  {#if history.length}<Button variant="secondary" on:click={goBack}><ArrowLeft size={14} aria-hidden="true" /> Back</Button>{/if}
  {#if comparison}<span class="revision-summary">{comparison.base.revision.slice(0, 10)} → {comparison.target.revision.slice(0, 10)}</span>{/if}
</nav>

<main class="workspace">
  <aside class="sidebar">
    <div class="filters"><input class="ui-control" bind:value={search} placeholder="Filter ID or title" aria-label="Filter documents" />
      <label class="checkbox"><input type="checkbox" bind:checked={hideSuperseded} on:change={() => localStorage.setItem('spec-review-hide-superseded', String(hideSuperseded))} /> Hide superseded</label>
      {#if comparison}<label class="checkbox"><input type="checkbox" bind:checked={changesOnly} on:change={() => localStorage.setItem('spec-review-changes-only', String(changesOnly))} /> Changes only</label>{/if}
    </div>
    <div class="category-list">
      {#each orderedCategoryEntries() as [key, label]}
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

<LinkChoiceDialog bind:this={linkDialog} choices={linkChoices} on:choose={(event) => chooseLink(event.detail)} />
{/if}
<SettingsDialog bind:this={settingsDialog} appearance={themeMode} on:appearancechange={(event) => setThemeMode(event.detail)} />
