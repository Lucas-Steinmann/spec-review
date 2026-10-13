<script>
  import { createEventDispatcher, onDestroy, tick } from 'svelte';
  import { X } from '@lucide/svelte';
  import Button from './Button.svelte';

  export let id;
  export let title;
  export let size = 'normal';
  export let initialFocus = 'input, select, button';
  export let showHeader = true;
  export let dismissOnBackdrop = false;
  let dialog;
  let returnFocus;
  const dispatch = createEventDispatcher();

  export async function showModal() {
    returnFocus = document.activeElement;
    dialog.showModal();
    await tick();
    dialog.querySelector(initialFocus)?.focus();
  }

  export function close() { dialog?.close(); }

  async function closed() {
    dispatch('close');
    await tick();
    if (returnFocus?.isConnected) returnFocus.focus();
  }

  function trapFocus(event) {
    if (event.key !== 'Tab') return;
    const controls = [...dialog.querySelectorAll('button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])')]
      .filter((node) => node.getClientRects().length && node.tabIndex >= 0);
    const first = controls[0];
    const last = controls.at(-1);
    if (!first) { event.preventDefault(); return; }
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }

  onDestroy(() => { if (dialog?.open) close(); });
</script>

<dialog
  bind:this={dialog}
  class="modal"
  class:compact={size === 'compact'}
  class:wide={size === 'wide'}
  aria-labelledby={showHeader ? `${id}-title` : undefined}
  aria-label={showHeader ? undefined : title}
  on:keydown={trapFocus}
  on:click={(event) => { if (dismissOnBackdrop && event.target === dialog) close(); }}
  on:close={closed}
  on:cancel
>
  {#if showHeader}
    <header class="modal-heading">
      <h2 id="{id}-title">{title}</h2>
      <Button variant="icon" compact aria-label="Close {title.toLowerCase()}" on:click={close}><X size={18} aria-hidden="true" /></Button>
    </header>
  {/if}
  <div class="modal-body"><slot /></div>
  {#if $$slots.actions}<footer class="modal-actions"><slot name="actions" /></footer>{/if}
</dialog>

<style>
  .modal {
    width: min(560px, calc(100vw - 32px));
    max-width: calc(100vw - 32px);
    max-height: calc(100dvh - 32px);
    overflow: auto;
    padding: 24px;
    border: 1px solid var(--line-strong);
    border-radius: var(--radius-lg);
    background: var(--surface-raised);
    color: var(--ink);
    box-shadow: var(--shadow);
  }
  .modal::backdrop { background: rgb(8 14 10 / 58%); backdrop-filter: blur(3px); }
  .compact { width: min(430px, calc(100vw - 32px)); }
  .modal-heading { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 22px; }
  h2 { min-width: 0; margin: 0; font-size: 18px; font-weight: 650; letter-spacing: -.025em; line-height: 1.3; }
  .modal-body { min-width: 0; }
  .modal-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; margin-top: 24px; }
  .wide { width: min(96vw, 1600px); height: min(94dvh, 1100px); max-width: 96vw; padding: 12px; }
  .wide[open] { display: flex; flex-direction: column; }
  .wide .modal-body { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 12px; }
  @media (max-width: 480px) { .modal { padding: 18px; } .wide { padding: 8px; } }
</style>
