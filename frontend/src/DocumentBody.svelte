<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import DiagramBlock from './DiagramBlock.svelte';
  import { renderMarkdown, renderMarkdownDiffLine } from './markdown.js';

  export let sections = [];
  export let diffAgainst = null;
  export let diffKind = 'added';
  const dispatch = createEventDispatcher();
  let body;

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
      {:else}
        <pre><code class={`language-${block.language || 'text'}`}>{block.text}</code></pre>
      {/if}
    {/each}
  {/each}
</div>
