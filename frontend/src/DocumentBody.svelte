<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import DiagramBlock from './DiagramBlock.svelte';
  import { renderMarkdown } from './markdown.js';

  export let sections = [];
  const dispatch = createEventDispatcher();
  let body;

  function handleClick(event) {
    const anchor = event.target.closest('a[data-review-href]');
    if (!anchor) return;
    event.preventDefault();
    dispatch('follow', { href: anchor.dataset.reviewHref });
  }

  onMount(() => {
    body.addEventListener('click', handleClick);
    return () => body.removeEventListener('click', handleClick);
  });
</script>

<div class="document-body" bind:this={body}>
  {#each sections as section}
    {#if section.heading}<h3>{section.heading}</h3>{/if}
    {#each section.blocks as block}
      {#if block.kind === 'markdown'}
        <div class="markdown">{@html renderMarkdown(block.text)}</div>
      {:else if block.kind === 'diagram'}
        <DiagramBlock {block} />
      {:else}
        <pre><code class={`language-${block.language || 'text'}`}>{block.text}</code></pre>
      {/if}
    {/each}
  {/each}
</div>
