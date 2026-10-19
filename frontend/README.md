# Frontend conventions

Svelte components own their interaction layout and scoped CSS. `style.css` holds theme tokens, the basic reset, page layout, and document formatting; it must not give every control inside a dialog button or field styles.

## Shared UI

- `ui/Dialog.svelte` wraps native `<dialog>`: bounded viewport size, scrolling, accessible heading, Escape, initial focus, Tab/Shift+Tab containment, and focus restoration. Use its actions slot for footer actions and its wide mode for the image viewer.
- `ui/Button.svelte` owns primary, secondary, quiet, icon, and choice appearances. The default button type is `button`; set `type="submit"` explicitly for form submission. Only the choice variant takes full width.
- `ui/FormField.svelte` owns label spacing. Text inputs and selects opt into `ui-control` from `ui/controls.css`; checkboxes keep their own treatment. Page-specific classes should control layout, not override component appearance.
- `components/` contains complete dialog contents. Keep API requests and source state out of the presentation primitives. `App.svelte` coordinates requests, source selection, and review navigation.

## Stories and mockups

Use Storybook to explore and document UI from the same Svelte components shipped by the application. Add stories under `src/**/*.stories.js`; compose examples from `ui/` and `components/` rather than recreating their markup in separate HTML or CSS. The Paper/Dark toolbar switch applies the app's theme tokens to every story. Keep application-level behavior in `App.svelte` and expose preview states by supplying deterministic fixtures to real components.

Run `npm run storybook` for the interactive component and UI catalog at `http://localhost:6006`, or `npm run build-storybook` to produce a static catalog. Browser overview, worktree, and review previews are stories of `App.svelte` with deterministic API fixtures in `src/stories/app-fixtures.js`; dialog screenshots use the compiled application with `spec/mockups/src/browser-dialogs.mjs`. Build both `dist` and Storybook, then run `node scripts/render_spec_mockups.mjs` from the repository root to refresh the committed previews. The browser mockups no longer have separate HTML or CSS copies. When a mockup exposes drift, update the shared Svelte component so the application and its story both change together.

Use theme tokens for color, spacing-related border radii, and focus treatment. Avoid descendant selectors such as `.dialog button` or `.dialog input`, specificity patches, and `!important` for control styling. Use grid with `minmax(0, 1fr)` for a field beside an action, so text fields can shrink while buttons retain their intended width.

## Verification

Run `npm run build` and `npm run test:e2e` after frontend changes. The browser suite starts isolated API/Vite servers; set `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` when using a system Chromium instead of Playwright's installed browser.

For dialog changes, run `e2e/dialog-layout.spec.js`. It exercises the real Svelte application at desktop, 360px, and 320px widths in Paper and Dark modes. It verifies label/control spacing, input width and height, compact actions, primary appearance, viewport containment, keyboard focus, and Escape. Inspect its screenshots, including errors and loading states when those change. Functional tests alone do not establish that a layout is correct.

`spec/mockups/src/browser-dialogs.mjs` supplies deterministic data for the real dialog previews and regressions. Build the frontend and Storybook, then run `node scripts/render_spec_mockups.mjs` from the repository root to update committed previews. Browser app previews render Storybook stories of the actual `App.svelte`; the terminal preview exports the running Textual app.
