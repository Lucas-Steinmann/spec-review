<script>
  import { createEventDispatcher } from 'svelte';
  import { ArrowUp, Folder } from '@lucide/svelte';
  import Button from '../ui/Button.svelte';
  import Dialog from '../ui/Dialog.svelte';
  import FormField from '../ui/FormField.svelte';

  export let source = 'local';
  export let path = '';
  export let specDir = 'spec';
  export let repository = '';
  export let listing = null;
  export let repositories = [];
  export let busy = false;
  export let error = '';
  let dialog;
  const dispatch = createEventDispatcher();
  export function showModal() { return dialog.showModal(); }
  export function close() { dialog.close(); }
</script>

<Dialog bind:this={dialog} id="add-repository" title="Add repository" initialFocus="select" on:close>
  <div class="add-form">
    <FormField label="Source">
      <select class="ui-control" aria-label="Source type" bind:value={source} on:change={() => dispatch('sourcechange')}>
        <option value="local">Local folder</option><option value="gh">GitHub repository</option>
      </select>
    </FormField>
    {#if source === 'local'}
      <form class="path-form" on:submit|preventDefault={() => dispatch('browse', path)}>
        <FormField label="Folder path"><input class="ui-control" aria-label="Folder path" bind:value={path} /></FormField>
        <Button type="submit" disabled={busy}>Go</Button>
      </form>
      {#if listing}
        <section class="folder-picker" aria-label="Folder browser">
          <Button compact disabled={busy || listing.parent === listing.path} on:click={() => dispatch('browse', listing.parent)}><ArrowUp size={15} aria-hidden="true" />Parent folder</Button>
          <div class="folder-browser">
            {#each listing.folders as folder (folder.path)}
              <Button variant="choice" disabled={busy} on:click={() => dispatch('browse', folder.path)}><Folder size={16} aria-hidden="true" /><span class="folder-name">{folder.name}</span></Button>
            {:else}<p class="hint">No readable subfolders.</p>{/each}
          </div>
        </section>
      {/if}
      <FormField label="Specification directory"><input class="ui-control" aria-label="Specification directory" bind:value={specDir} /></FormField>
      <p class="hint">Select a folder on the machine running spec-review. The specification directory is relative to that folder.</p>
    {:else}
      <FormField label="Repository"><select class="ui-control" bind:value={repository}>{#each repositories as item (item.full_name)}<option value={item.full_name}>{item.full_name}</option>{/each}</select></FormField>
    {/if}
    {#if busy}<p class="status" role="status">Loading…</p>{/if}
    {#if error}<p class="error" role="alert">{error}</p>{/if}
  </div>
  <svelte:fragment slot="actions">
    <Button on:click={close}>Cancel</Button>
    <Button variant="primary" disabled={busy || (source === 'local' ? !path : !repository)} on:click={() => dispatch('add')}>Add repository</Button>
  </svelte:fragment>
</Dialog>

<style>
  .add-form { display: grid; gap: 18px; }
  .path-form { min-width: 0; display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 10px; }
  .folder-picker { min-width: 0; display: grid; gap: 10px; }
  .folder-picker > :global(button) { justify-self: start; }
  .folder-browser { max-height: min(240px, 30dvh); min-width: 0; overflow: auto; display: grid; gap: 6px; padding: 4px; border: 1px solid var(--line); border-radius: var(--radius-sm); }
  .folder-name { min-width: 0; overflow-wrap: anywhere; }
  .hint, .status, .error { margin: 0; font-size: 11px; line-height: 1.6; overflow-wrap: anywhere; }
  .hint { color: var(--ink-muted); }
  .error { color: var(--negative); }
</style>
