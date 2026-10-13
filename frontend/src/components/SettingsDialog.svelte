<script>
  import { createEventDispatcher } from 'svelte';
  import Button from '../ui/Button.svelte';
  import Dialog from '../ui/Dialog.svelte';
  import FormField from '../ui/FormField.svelte';
  export let appearance = 'system';
  let dialog;
  const dispatch = createEventDispatcher();
  export function showModal() { return dialog.showModal(); }
  export function close() { dialog.close(); }
</script>

<Dialog bind:this={dialog} id="settings" title="Settings" size="compact" initialFocus="select" on:close>
  <div class="appearance-setting">
    <FormField label="Appearance">
      <select class="ui-control" aria-label="Appearance" value={appearance} on:change={(event) => dispatch('appearancechange', event.currentTarget.value)}>
        <option value="system">System</option><option value="paper">Paper</option><option value="dark">Dark</option>
      </select>
    </FormField>
    <p>Choose how the workspace looks. System follows your device’s appearance.</p>
  </div>
  <Button slot="actions" variant="primary" on:click={close}>Done</Button>
</Dialog>

<style>
  .appearance-setting { display: grid; gap: 10px; }
  p { margin: 0; color: var(--ink-muted); font-size: 12px; line-height: 1.6; }
</style>
