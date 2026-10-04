<script>
  import { onMount } from 'svelte';
  export let block;
  let image = '';
  let error = '';
  let loading = true;

  onMount(async () => {
    try {
      const response = await fetch('/api/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: block.language, text: block.text }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Diagram renderer failed');
      image = result.data_url;
    } catch (problem) {
      error = problem.message || String(problem);
    } finally {
      loading = false;
    }
  });
</script>

<figure class="diagram">
  <pre><code class={`language-${block.language || 'text'}`}>{block.text}</code></pre>
  {#if image}
    <img src={image} alt={`${block.language} diagram`} />
  {:else if loading}
    <figcaption>Rendering diagram…</figcaption>
  {:else if error}
    <figcaption class="diagram-error">{error}</figcaption>
  {/if}
</figure>
