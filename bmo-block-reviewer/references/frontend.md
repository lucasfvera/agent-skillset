# Frontend review rules (`frontend`)

Apply when the diff touches UI components, signals/hooks, reactive forms or view state, templates, routes, accessibility, or styling/CSS/SCSS.

## 1. Strict issues (`[issue]`)

Check these first. Every violation is a correctness, accessibility, routing, or UX state bug.

- **[concurrent-submit-guard]** Guard async submit and action handlers with an early return when an in-flight or loading state/signal is active (since disabled form controls can clear invalid flags and custom host click bindings still fire), and delegate error banner state to the shared form validator so errors clear on user input.
- **[preserve-semantic-roles-and-a11y]** Preserve native HTML semantics and WCAG contracts: wrap link lists in `<ul><li>` rather than placing `role="listitem"` on `<a>`, keep sequential `<h1>`–`<h3>` headings, pair every form input with a `<label>`, start `aria-label` with visible link text, trap focus inside modals, and announce one-way status transitions via `aria-live="polite"` outside ticking timers.
- **[preserve-routes-during-file-moves]** Preserve existing URL route paths when moving or reorganizing component files unless a route change is explicitly part of the requirement.
- **[constructor-init-and-synchronous-signal-seed]** Seed signals directly from synchronous initial state at declaration and run one-time listener setup in `constructor` rather than `ngOnInit` when no `input()` values are required, avoiding one-shot promises that race persistent state listeners.
- **[parent-form-group-cross-field-validators]** Attach cross-field reactive form validators to the parent `FormGroup` returning group-level validation errors rather than mutating child control error states manually, and extract reusable validators into a tested shared utility.
- **[no-fallback-unproduced-states]** Render only states and notification types the upstream pipeline actually emits; never invent default tickers or assets when a lookup is unresolved.
- **[suppress-unresolved-display]** Return the raw identifier from lookup resolvers during catalog races and suppress rendering at the call site until resolved, rather than returning empty sentinel strings.
- **[verify-domain-guards]** Verify multi-phase event sequences before simplifying or removing domain state guards, since early events may carry sentinel values before the final state arrives.

## 2. Style & conventions (`[style]`)

Check these after Pass 1. Align the code to these patterns without crowding out `[issue]` findings.

- **[single-dom-across-viewports]** Render one shared DOM tree across mobile/desktop viewports, variants, and conditional branches, adapting layout via CSS breakpoints, modifiers, or template bindings rather than duplicating component markup or copy.
- **[encapsulate-component-member-visibility]** Mark component properties, signals, and methods used only by the class or its template as `protected` (and `readonly` where applicable), reserving `public` for external APIs or framework contracts.
- **[infer-primitive-signal-types]** Omit explicit primitive generic type arguments on signals and inputs (`signal(false)`, `input(false)`) when TypeScript infers the type from the default value.
- **[union-variant-over-boolean-mode-flags]** Model mutually exclusive presentation modes with a single union `variant` input rather than multiple boolean flags or caller-coupled props like `isLoggedIn`.
- **[colocate-component-constants-and-inputs]** Extract static display data arrays and companion interfaces into a colocated `*.constants.ts` file, and expose configurable collections on the component as `input()` signals defaulted to those constants.
- **[omit-default-standalone-true]** Omit `standalone: true` and empty `imports: []` arrays from `@Component` and `@Directive` decorators in Angular v19+ projects where standalone is default.
- **[use-ng-optimized-image]** Use `NgOptimizedImage` (`ngSrc`) with explicit `width` and `height` (or `fill`) on static images, adding `priority` to above-the-fold LCP graphics.
- **[component-host-metadata-over-decorators]** Declare host event listeners and property bindings in the `host` metadata option of `@Component` or `@Directive` rather than `@HostListener` or `@HostBinding` method decorators.
- **[feature-flag-signals-and-shared-primitives]** Track feature flags in components with a `readonly enable<Feature>` signal, hide gated UI actions completely when disabled, and reuse shared UI primitives (such as shared button or modal components) over raw HTML controls.
- **[match-sibling-ui-patterns]** Match the working layout, scroll, and container pattern from sibling components in the same feature before inventing a new structure.
- **[avoid-useeffect-derived-state]** Compute derived state during render or via declarative form bindings (such as `react-hook-form` `values`) rather than syncing state through `useEffect` and refs.
- **[validate-from-handlers-not-effects]** Trigger user-input validation inside event handlers (`onChange`, `onBlur`, `onSubmit`); reserve `useEffect` for externally updated derived values that never fire those handlers.
- **[reuse-existing-state]** Derive remount keys and UI triggers from existing state or props instead of introducing a parallel state variable solely for that trigger.
- **[extend-via-optional-props]** Add an optional prop to the shared underlying component when one caller needs a layout or styling variation, rather than adding a thin wrapper component.
- **[one-shared-hook-not-domain-copy]** Keep shared client hooks in the shared hooks module and use a compatibility re-export for old import paths rather than copying the hook into a domain folder.
- **[single-loading-skeleton]** Hide dependent fields until the primary load finishes rather than rendering a second loading skeleton beside the existing one.
- **[prefer-design-tokens]** Use existing design-system tokens and breakpoint mixins for color, spacing, and typography; when a design needs a new shade, add a WCAG AA contrast-compliant token to the shared palette rather than hardcoding hex/RGB literals, and annotate any unavoidable arbitrary utility value.
