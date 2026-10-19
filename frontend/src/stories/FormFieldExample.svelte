<script>
  import FormField from '../ui/FormField.svelte';
</script>

<div class="example">
  <FormField label="Repository name"><input class="ui-control" value="acme/spec-review" /></FormField>
  <FormField label="Revision"><select class="ui-control"><option>main</option><option>feature/review-ui</option></select></FormField>
</div>

<style>
  .example { width: min(420px, calc(100vw - 48px)); display: grid; gap: 16px; padding: 24px; background: var(--canvas); }
</style>
