<script>
  import { onMount } from 'svelte';
  import AddRepositoryDialog from '../components/AddRepositoryDialog.svelte';

  let dialog;
  onMount(() => dialog.showModal());
</script>

<div class="stage">
  <AddRepositoryDialog
    bind:this={dialog}
    source="local"
    path="/home/reviewer/projects/spec-review"
    specDir="spec"
    listing={{ path: '/home/reviewer/projects', parent: '/home/reviewer', folders: [
      { name: 'spec-review', path: '/home/reviewer/projects/spec-review' },
      { name: 'a-folder-with-a-long-name-that-wraps-cleanly', path: '/home/reviewer/projects/a-folder-with-a-long-name-that-wraps-cleanly' },
    ] }}
  />
</div>

<style>
  .stage { min-height: 500px; padding: 24px; background: var(--canvas); }
</style>
