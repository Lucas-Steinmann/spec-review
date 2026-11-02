<script>
  export let block;
  export let otherText = null;
  $: counts = (() => {
    const result = new Map();
    for (const line of (otherText || '').split('\n')) result.set(line, (result.get(line) || 0) + 1);
    return result;
  })();
  $: lines = block.text.split('\n').map((text) => {
    const remaining = counts.get(text) || 0;
    if (remaining) counts.set(text, remaining - 1);
    return { text, changed: otherText !== null && !!text.trim() && !remaining };
  });
</script>

<pre><code class={`language-${block.language || 'text'}`}>{#each lines as line, i}<span class:changed-line={line.changed} class="code-diff-line">{line.text}{i < lines.length - 1 ? '\n' : ''}</span>{/each}</code></pre>
