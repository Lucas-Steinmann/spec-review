<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { Maximize, RotateCcw, X, ZoomIn, ZoomOut } from '@lucide/svelte';
  import Button from './ui/Button.svelte';
  import Dialog from './ui/Dialog.svelte';
  import DiagramBlock from './DiagramBlock.svelte';
  import { renderMarkdown, renderMarkdownDiffLine } from './markdown.js';

  export let sections = [];
  export let diffAgainst = null;
  export let diffKind = 'added';
  const dispatch = createEventDispatcher();
  let body;
  let imageViewer;
  let viewerSource = '';
  let viewerAlt = '';
  let fitWidth = 0;
  let zoom = 1;
  let imageReturnFocus;
  $: viewerWidth = fitWidth ? Math.round(fitWidth * zoom) : 0;

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
      const remaining = counts.get(line) || 0;
      if (remaining) {
        counts.set(line, remaining - 1);
        return 'context';
      }
      return 'changed';
    });
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

  function openImage(image) {
    viewerSource = image.currentSrc || image.src;
    viewerAlt = image.alt || 'Specification image';
    imageReturnFocus = image;
    fitWidth = 0;
    zoom = 1;
    imageViewer?.showModal();
  }

  function fitViewerImage(event) {
    const image = event.currentTarget;
    if (!image.naturalWidth || !image.naturalHeight) return;
    const availableWidth = Math.max(240, window.innerWidth - 100);
    const availableHeight = Math.max(180, window.innerHeight - 180);
    fitWidth = Math.round(Math.min(image.naturalWidth, availableWidth, availableHeight * image.naturalWidth / image.naturalHeight));
  }

  function changeZoom(factor) {
    zoom = Math.min(5, Math.max(0.25, Math.round(zoom * factor * 100) / 100));
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
            {#each block.text.split('\n') as line, lineIndex}
              <div class:changed-line={changes[lineIndex] === 'changed'} class="markdown-diff-line">
                {@html changes[lineIndex] === 'changed'
                  ? renderMarkdownDiffLine(line, diffAgainst?.[sectionIndex]?.blocks?.[blockIndex]?.text?.split('\n')?.[lineIndex] || '', diffKind)
                  : renderMarkdown(line || ' ')}
              </div>
            {/each}
          </div>
        {:else}
          <div class="markdown">{@html renderMarkdown(block.text)}</div>
        {/if}
      {:else if block.kind === 'diagram'}
        <DiagramBlock {block} />
      {:else if block.kind === 'image'}
        <figure class="spec-image">
          <img src={block.text} alt={block.language || 'Specification visual'} />
          {#if block.language}<figcaption>{block.language}</figcaption>{/if}
        </figure>
      {:else}
        <pre><code class={`language-${block.language || 'text'}`}>{block.text}</code></pre>
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
      <Button variant="icon" compact aria-label="Zoom in" title="Zoom in" disabled={zoom >= 5} on:click={() => changeZoom(1.25)}><ZoomIn size={17} aria-hidden="true" /></Button>
      <Button variant="icon" compact aria-label="Fit to window" title="Fit to window" on:click={() => zoom = 1}><Maximize size={16} aria-hidden="true" /></Button>
      <Button variant="icon" compact aria-label="Close image viewer" title="Close image viewer" on:click={closeImageViewer}><X size={18} aria-hidden="true" /></Button>
    </div>
  </div>
  <div class="image-viewer-viewport">
    <img class="image-viewer-image" src={viewerSource} alt={viewerAlt} width={viewerWidth || undefined} on:load={fitViewerImage} />
  </div>
</Dialog>
