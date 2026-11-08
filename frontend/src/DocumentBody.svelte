<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { Maximize, RotateCcw, X, ZoomIn, ZoomOut } from '@lucide/svelte';
  import Button from './ui/Button.svelte';
  import Dialog from './ui/Dialog.svelte';
  import CodeBlock from './CodeBlock.svelte';
  import DiagramBlock from './DiagramBlock.svelte';
  import { renderMarkdown, renderMarkdownDiff } from './markdown.js';

  export let sections = [];
  export let diffAgainst = null;
  export let diffKind = 'added';
  const dispatch = createEventDispatcher();
  let body;
  let imageViewer;
  let viewerViewport;
  let viewerImage;
  let viewerSource = '';
  let viewerAlt = '';
  let fitWidth = 0;
  let zoom = 1;
  let imageReturnFocus;
  $: viewerWidth = fitWidth ? fitWidth * zoom : 0;

  function otherMarkdown(sectionIndex, blockIndex) {
    if (!diffAgainst) return null;
    const other = diffAgainst?.[sectionIndex]?.blocks?.[blockIndex];
    return other?.kind === 'markdown' ? other.text : '';
  }

  function lineChanges(text, otherText) {
    if (otherText === null || otherText === undefined) return null;
    const counts = new Map();
    for (const line of otherText.split('\n')) counts.set(line, (counts.get(line) || 0) + 1);
    return text.split('\n').map((line) => {
      if (!line.trim()) return 'context';
      const remaining = counts.get(line) || 0;
      if (remaining) {
        counts.set(line, remaining - 1);
        return 'context';
      }
      return 'changed';
    });
  }

  function imageIdentity(block) {
    const url = new URL(block.text, window.location.href);
    if (['/api/local/asset', '/api/gh/asset'].includes(url.pathname)) {
      url.searchParams.delete('ref');
      url.searchParams.sort();
    }
    return `${url.href}\n${block.language || ''}`;
  }

  function imageChanged(block, sectionIndex) {
    if (!diffAgainst) return false;
    return !diffAgainst[sectionIndex]?.blocks?.some((other) =>
      other.kind === 'image' && imageIdentity(other) === imageIdentity(block));
  }

  function handleClick(event) {
    const anchor = event.target.closest('a[data-review-href]');
    if (anchor) {
      event.preventDefault();
      dispatch('follow', { href: anchor.dataset.reviewHref });
      return;
    }
    const image = event.target.closest('img');
    if (image && body.contains(image)) openImage(image);
  }

  function handleKeydown(event) {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const image = event.target.closest('img[role="button"]');
    if (!image || !body.contains(image)) return;
    event.preventDefault();
    openImage(image);
  }

  function prepareImages() {
    for (const image of body.querySelectorAll('img')) {
      image.tabIndex = 0;
      image.setAttribute('role', 'button');
      image.setAttribute('aria-haspopup', 'dialog');
      image.setAttribute('aria-label', `${image.alt || 'Specification image'} (open image viewer)`);
      image.title = 'Open image viewer';
    }
  }

  async function openImage(image) {
    viewerSource = image.currentSrc || image.src;
    viewerAlt = image.alt || 'Specification image';
    imageReturnFocus = image;
    fitWidth = 0;
    zoom = 1;
    await imageViewer?.showModal();
    fitViewerImage();
  }

  function fitViewerImage() {
    const image = viewerImage;
    if (!image?.naturalWidth || !image.naturalHeight || !viewerViewport) return;
    const bounds = viewerViewport.getBoundingClientRect();
    const availableWidth = Math.min(viewerViewport.clientWidth, bounds.width);
    const availableHeight = Math.min(viewerViewport.clientHeight, bounds.height);
    if (!availableWidth || !availableHeight) return;
    fitWidth = Math.floor(Math.min(availableWidth, availableHeight * image.naturalWidth / image.naturalHeight));
  }

  function changeZoom(factor) {
    zoom = Math.min(20, Math.max(0.25, zoom * factor));
  }

  function handleWheel(event) {
    if (event.ctrlKey || event.metaKey) {
      event.preventDefault();
      const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? event.currentTarget.clientHeight : 1;
      changeZoom(Math.exp(-event.deltaY * unit * 0.002));
    } else if (event.shiftKey) {
      event.preventDefault();
      const viewport = event.currentTarget;
      const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientWidth : 1;
      viewport.scrollLeft += (event.deltaX || event.deltaY) * unit;
    }
  }

  function closeImageViewer() {
    imageViewer?.close();
  }

  onMount(() => {
    body.addEventListener('click', handleClick);
    body.addEventListener('keydown', handleKeydown);
    const imageObserver = new MutationObserver(prepareImages);
    imageObserver.observe(body, { childList: true, subtree: true });
    prepareImages();
    return () => {
      body.removeEventListener('click', handleClick);
      body.removeEventListener('keydown', handleKeydown);
      imageObserver.disconnect();
    };
  });
</script>

<div class="document-body" bind:this={body}>
  {#each sections as section, sectionIndex}
    {#if section.heading}<h3>{section.heading}</h3>{/if}
    {#each section.blocks as block, blockIndex}
      {#if block.kind === 'markdown'}
        {@const changes = lineChanges(block.text, otherMarkdown(sectionIndex, blockIndex))}
        {#if changes}
          <div class="markdown markdown-diff">
            {@html renderMarkdownDiff(block.text, otherMarkdown(sectionIndex, blockIndex), diffKind, changes)}
          </div>
        {:else}
          <div class="markdown">{@html renderMarkdown(block.text)}</div>
        {/if}
      {:else if block.kind === 'diagram'}
        <DiagramBlock {block} otherText={diffAgainst === null ? null : (diffAgainst?.[sectionIndex]?.blocks?.[blockIndex]?.kind === block.kind ? diffAgainst[sectionIndex].blocks[blockIndex].text : '')} />
      {:else if block.kind === 'image'}
        <figure class="spec-image" class:diff-image={diffAgainst !== null} class:changed-image={imageChanged(block, sectionIndex)} class:removed-image={diffKind === 'removed'}>
          <img src={block.text} alt={block.language || 'Specification visual'} />
          {#if block.language}<figcaption>{block.language}</figcaption>{/if}
        </figure>
      {:else}
        <CodeBlock {block} otherText={diffAgainst === null ? null : (diffAgainst?.[sectionIndex]?.blocks?.[blockIndex]?.kind === block.kind ? diffAgainst[sectionIndex].blocks[blockIndex].text : '')} />
      {/if}
    {/each}
  {/each}
</div>

<Dialog bind:this={imageViewer} id="image-viewer" title="Image viewer" size="wide" showHeader={false} dismissOnBackdrop initialFocus="[aria-label='Close image viewer']" on:close={() => imageReturnFocus?.focus()}>
  <div class="image-viewer-toolbar">
    <p class="image-viewer-title" title={viewerAlt}>{viewerAlt}</p>
    <div class="image-viewer-actions">
      <Button variant="icon" compact aria-label="Zoom out" title="Zoom out" disabled={zoom <= 0.25} on:click={() => changeZoom(1 / 1.25)}><ZoomOut size={17} aria-hidden="true" /></Button>
      <output aria-live="polite">{Math.round(zoom * 100)}%</output>
      <Button variant="icon" compact aria-label="Zoom in" title="Zoom in" disabled={zoom >= 20} on:click={() => changeZoom(1.25)}><ZoomIn size={17} aria-hidden="true" /></Button>
      <Button variant="icon" compact aria-label="Fit to window" title="Fit to window" on:click={() => { zoom = 1; fitViewerImage(); }}><Maximize size={16} aria-hidden="true" /></Button>
      <Button variant="icon" compact aria-label="Close image viewer" title="Close image viewer" on:click={closeImageViewer}><X size={18} aria-hidden="true" /></Button>
    </div>
  </div>
  <div class="image-viewer-viewport" bind:this={viewerViewport} on:wheel|nonpassive={handleWheel}>
    <img bind:this={viewerImage} class="image-viewer-image" src={viewerSource} alt={viewerAlt} width={viewerWidth || undefined} on:load={fitViewerImage} />
  </div>
</Dialog>
