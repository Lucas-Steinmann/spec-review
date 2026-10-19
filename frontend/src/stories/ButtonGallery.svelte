<script>
  import Button from '../ui/Button.svelte';
</script>

<section class="gallery" aria-label="Button variants">
  <div><Button variant="primary">Primary action</Button><Button>Secondary action</Button><Button variant="quiet">Quiet action</Button></div>
  <div><Button variant="choice">Choose a repository</Button><Button compact>Compact action</Button><Button disabled>Disabled</Button></div>
</section>

<style>
  .gallery { display: grid; gap: 16px; padding: 24px; background: var(--canvas); color: var(--ink); }
  .gallery > div { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
</style>
