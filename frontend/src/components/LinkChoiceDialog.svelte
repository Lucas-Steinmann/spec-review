<script>
  import { createEventDispatcher } from 'svelte';
  import Button from '../ui/Button.svelte';
  import Dialog from '../ui/Dialog.svelte';
  export let choices = [];
  let dialog;
  const dispatch = createEventDispatcher();
  export function showModal() { return dialog.showModal(); }
  export function close() { dialog.close(); }
</script>

<Dialog bind:this={dialog} id="link-choice" title="Choose a linked artifact" initialFocus="[data-link-choice]">
  <div class="choices">
    {#each choices as choice (choice.id)}
      <Button variant="choice" data-link-choice on:click={() => dispatch('choose', choice.id)}><strong>{choice.id}</strong><span>{choice.title}</span></Button>
    {/each}
  </div>
  <Button slot="actions" on:click={close}>Cancel</Button>
</Dialog>

<style>
  .choices { display: grid; gap: 8px; }
  span { color: var(--ink-muted); font-size: 11px; overflow-wrap: anywhere; }
</style>
