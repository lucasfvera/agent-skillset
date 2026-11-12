# Frontend review rules (`frontend`)

Apply when the diff touches UI components, client hooks, form or view state, templates, or styling/CSS.

## 1. Strict issues (`[issue]`)

Check these first. Every violation is a correctness or UX state bug.

- **[concurrent-submit-guard]** Guard async submit and action handlers with an in-flight or loading check so rapid clicks cannot fire duplicate requests.
- **[no-fallback-unproduced-states]** Render only states and notification types the upstream pipeline actually emits; never invent default tickers or assets when a lookup is unresolved.
- **[suppress-unresolved-display]** Return the raw identifier from lookup resolvers during catalog races and suppress rendering at the call site until resolved, rather than returning empty sentinel strings.
- **[verify-domain-guards]** Verify multi-phase event sequences before simplifying or removing domain state guards, since early events may carry sentinel values before the final state arrives.

## 2. Style & conventions (`[style]`)

Check these after Pass 1. Align the code to these patterns without crowding out `[issue]` findings.

- **[single-dom-across-viewports]** Render one shared DOM tree across viewports, variants, and conditional branches, adapting layout via CSS or bindings rather than duplicating component markup or copy.
- **[match-sibling-ui-patterns]** Match the working layout, scroll, and container pattern from sibling components in the same feature before inventing a new structure.
- **[avoid-useeffect-derived-state]** Compute derived state during render or via declarative form bindings (such as `react-hook-form` `values`) rather than syncing state through `useEffect` and refs.
- **[validate-from-handlers-not-effects]** Trigger user-input validation inside event handlers (`onChange`, `onBlur`, `onSubmit`); reserve `useEffect` for externally updated derived values that never fire those handlers.
- **[reuse-existing-state]** Derive remount keys and UI triggers from existing state or props instead of introducing a parallel state variable solely for that trigger.
- **[extend-via-optional-props]** Add an optional prop to the shared underlying component when one caller needs a layout or styling variation, rather than adding a thin wrapper component.
- **[one-shared-hook-not-domain-copy]** Keep shared client hooks in the shared hooks module and use a compatibility re-export for old import paths rather than copying the hook into a domain folder.
- **[single-loading-skeleton]** Hide dependent fields until the primary load finishes rather than rendering a second loading skeleton beside the existing one.
- **[prefer-design-tokens]** Use existing design-system tokens for color, spacing, and typography; annotate any unavoidable arbitrary utility value with why no token fits.
