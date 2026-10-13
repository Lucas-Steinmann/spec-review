<script>
  export let variant = 'secondary';
  export let type = 'button';
  export let disabled = false;
  export let element = null;
  export let compact = false;
  let className = '';
  export { className as class };
</script>

<button
  bind:this={element}
  {...$$restProps}
  {type}
  {disabled}
  class="ui-button {className}"
  class:primary={variant === 'primary'}
  class:quiet={variant === 'quiet'}
  class:icon={variant === 'icon'}
  class:choice={variant === 'choice'}
  class:compact
  on:click
>
  <slot />
</button>

<style>
  .ui-button {
    flex: none;
    min-height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 8px 13px;
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    background: var(--surface);
    color: var(--ink-secondary);
    font-size: 12px;
    font-weight: 650;
    line-height: 1.4;
    text-decoration: none;
    cursor: pointer;
  }
  .ui-button:hover:not(:disabled) { background: var(--surface-hover); border-color: var(--line-strong); }
  .primary { border-color: transparent; background: var(--accent); color: var(--accent-ink); box-shadow: 0 1px 2px rgb(15 30 20 / 12%); }
  .primary:hover:not(:disabled) { border-color: transparent; background: var(--accent-hover); }
  .quiet { background: transparent; border-color: transparent; }
  .quiet:hover:not(:disabled) { border-color: transparent; background: var(--surface-subtle); }
  .icon { width: 36px; height: 36px; padding: 0; }
  .choice { width: 100%; min-width: 0; min-height: 40px; justify-content: flex-start; text-align: left; font-weight: 500; }
  .compact { min-height: 32px; padding: 6px 9px; font-size: 11px; }
  .icon.compact { width: 32px; height: 32px; padding: 0; }
  .ui-button:disabled { cursor: not-allowed; opacity: .55; }
</style>
