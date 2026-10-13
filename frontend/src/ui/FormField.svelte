<script>
  export let label;
  export let compact = false;
  let className = '';
  export { className as class };
</script>

<label class="field {className}" class:compact>
  <span class="field-label">{label}</span>
  <slot />
</label>

<style>
  .field { min-width: 0; display: grid; gap: 7px; margin: 0; color: var(--ink-secondary); font-size: 12px; font-weight: 500; }
  .field-label { color: var(--ink-muted); font-size: 11px; font-weight: 650; line-height: 1.4; }
  .compact { gap: 5px; }
  .compact .field-label { font-size: 10px; letter-spacing: .07em; text-transform: uppercase; }
</style>
