# Block reviewer learnings catalog

Abstract guidelines distilled from PR review session captures in `inbox/`. **Do not paste verbatim comments here.**

Pending captures live in [`bmo-update-block-reviewer-skill/inbox/pending/`](../../bmo-update-block-reviewer-skill/inbox/pending/). Processed captures move to [`inbox/actioned/`](../../bmo-update-block-reviewer-skill/inbox/actioned/). Run [`bmo-update-block-reviewer-skill`](../../bmo-update-block-reviewer-skill/SKILL.md) to merge pending feedback into this catalog.

The block reviewer skill stays short. See [promotion rules](../../bmo-update-block-reviewer-skill/references/promotion-rules.md) for what moves into [`SKILL.md`](../SKILL.md).

---

## Typing

### strict-equality

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Always use strict equality when comparing values; never use loose equality. |
| **Rationale** | Loose equality hides type coercion bugs and obscures intent when distinguishing null from undefined. |
| **Sources** | roxom-markets/roxtopia#833, roxom-markets/roxtopia#841, roxom-markets/roxtopia#843, roxom-markets/roxtopia#859 |
| **Promoted** | yes (already in block-reviewer) |

### schema-narrow-types

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Prefer schema-defined narrow types at message boundaries instead of broad unions when upstream validation already constrains the shape. |
| **Rationale** | Narrow types document the real contract and remove unnecessary runtime branching. |
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

### test-contract-types

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Type test fixtures with the actual contract types from the producing service rather than loose object shapes. |
| **Rationale** | Contract-typed fixtures catch shape drift at compile time and document the expected integration boundary. |
| **Sources** | roxom-markets/door#218, roxom-markets/roxtarsverse#751, roxom-markets/window#801 |
| **Promoted** | yes (already in block-reviewer) |

### test-typed-stubs

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Prefer explicit typed no-op stubs over never or unknown shortcuts in test harnesses. |
| **Rationale** | never and unknown hide missing dependency shapes and diverge from how other tests stub the same surface. |
| **Sources** | roxom-markets/roxtarsverse#751 |
| **Promoted** | no |

### zod-parse-contract-payload

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Do not manually re-map successful contract payloads field-by-field; if the boundary needs validation or key stripping, parse with the existing Zod schema pattern. |
| **Rationale** | Hand-built projections duplicate the contract and drift from how other handlers validate the same shape. |
| **Sources** | roxom-markets/window#800 |
| **Promoted** | no |

### no-locator-type-assertions

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Do not cast queried elements when the locator and matcher already provide the type. |
| **Rationale** | Extra assertions hide whether the query already returned the right element and fight the testing library's types. |
| **Sources** | roxom-markets/roxtopia#1074 |
| **Promoted** | yes (already in block-reviewer) |

### catch-unknown-not-any

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Catch errors as unknown and narrow with instanceof Error; never type the catch binding as any. |
| **Rationale** | any on catch hides the real error shape and diverges from how sibling handlers already narrow failures. |
| **Sources** | roxom-markets/roxtarsverse#824 |
| **Promoted** | yes (already in block-reviewer) |

## Tests

### test-realistic-fixtures

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Use realistic fixture values — UUID v4 for ID fields, real enum members, plausible amounts — not placeholder strings like tx-123 or user-1. |
| **Rationale** | Realistic fixtures mirror production data shapes and catch type or format assumptions early. |
| **Sources** | roxom-markets/roxtopia#833, roxom-markets/roxtopia#832, roxom-markets/window#801 |
| **Promoted** | yes (already in block-reviewer) |

### test-canonical-urls

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Assert canonical production URLs in tests rather than alternate forms that only work through redirects. |
| **Rationale** | Redirect-dependent assertions can pass while the canonical route is broken if redirect logic changes. |
| **Sources** | roxom-markets/roxtopia#833 |
| **Promoted** | no |

### test-real-logger-off

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Prefer the real logger component with LogLevel.OFF and spies over mocking the logger when asserting log behavior. |
| **Rationale** | Exercises the real logging path without console noise and avoids brittle mock shapes. |
| **Sources** | roxom-markets/door#218 |
| **Promoted** | no |

### test-aaa-pattern

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Structure unit tests with Arrange, Act, and Assert blocks, keeping setup variables separate from the call and expectations. |
| **Rationale** | Separating phases makes intent obvious and keeps assertions readable. |
| **Sources** | roxom-markets/roxtopia#859 |
| **Promoted** | no |

### reuse-shared-test-mocks

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Reuse shared suite mocks and render helpers for common dependencies instead of inventing one-off mock shapes or local provider wrappers in a single spec. |
| **Rationale** | Shared mocks and renderers keep harness behavior consistent and avoid drift from the suite baseline. |
| **Sources** | roxom-markets/roxtarsverse#751, roxom-markets/window#801, roxom-markets/roxtopia#1162 |
| **Promoted** | yes (already in block-reviewer) |

### test-unit-owned-contract

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | When a dependency is mocked, assert the unit's own contract — methods called, arguments, HTTP projection, owned status codes — not payload fields the mock was hardcoded to return. |
| **Rationale** | Re-asserting mocked upstream values tests the mock, not the service under test. |
| **Sources** | roxom-markets/window#800 |
| **Promoted** | no |

### no-non-contract-negative-tests

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Do not assert negatives for product or timeline choices, route constants, implementation details that are not a hard contract, or that a removed path is absent unless the change is a regression fix. |
| **Rationale** | Those assertions lock in incidental decisions and add noise without protecting a real invariant. |
| **Sources** | roxom-markets/window#801, roxom-markets/roxtarsverse#824, roxom-markets/roxtopia#1175 |
| **Promoted** | yes (already in block-reviewer) |

### test-unauthenticated-when-middleware-allows

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Keep unauthenticated-path tests when route middleware does not actually reject missing sessions; do not assume every account endpoint is auth-gated the same way. |
| **Rationale** | Sibling handlers differ in middleware, so a missing user can be a real request shape rather than an impossible state. |
| **Sources** | roxom-markets/window#800 |
| **Promoted** | no |

### integration-tests-match-production

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Write integration tests against the shared suite factory and generated client the way production consumes the API; do not boot a parallel harness, call handlers directly, or wrap the client in test-only helpers or extra Promises. |
| **Rationale** | One-off harnesses and handler wrappers drift from real consumption and hide setup the rest of the suite already owns. |
| **Sources** | roxom-markets/roxtarsverse#823, roxom-markets/roxtarsverse#824, roxom-markets/roxtarsverse#825 |
| **Promoted** | yes (already in block-reviewer) |

### no-overlapping-method-tests

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Do not re-test behavior owned by another method or already covered in a related change; keep the spec scoped to the code under review. |
| **Rationale** | Overlapping cases duplicate coverage, couple unrelated PRs, and make the spec harder to trust. |
| **Sources** | roxom-markets/roxtarsverse#824, roxom-markets/roxtarsverse#825 |
| **Promoted** | yes (already in block-reviewer) |

### no-unproven-indirect-assertions

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Do not keep leak or security assertions that only watch indirect side channels unless injecting the leak has been shown to fail the test. |
| **Rationale** | Indirect spies can pass while the behavior they claim to protect is never actually exercised. |
| **Sources** | roxom-markets/roxtarsverse#824 |
| **Promoted** | no |

### test-user-event

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Use user-event for interactions that matter; avoid fireEvent unless there is a clear reason it cannot drive the case. |
| **Rationale** | fireEvent skips the user path and misses the same timing and event sequence production sees. |
| **Sources** | roxom-markets/roxtopia#1074 |
| **Promoted** | yes (already in block-reviewer) |

### no-css-class-assertions

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Do not assert CSS class names or visual styling in unit tests; cover behavior instead, and drop the case if it cannot be tested that way. |
| **Rationale** | Class and style assertions are brittle and are not what these suites are for. |
| **Sources** | roxom-markets/roxtopia#1182, roxom-markets/roxtopia#1197 |
| **Promoted** | yes |

### no-self-asserting-constants

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Do not write tests that only assert a hardcoded constant, alias, or reassignment against itself. |
| **Rationale** | Those tests pass without exercising behavior and lock in incidental wiring. |
| **Sources** | roxom-markets/roxtopia#1196, roxom-markets/roxtopia#1231 |
| **Promoted** | yes |

### test-live-export-not-leftover

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Test the live exported copy of a component; do not add or keep specs that only cover an unused leftover duplicate. |
| **Rationale** | Leftover copies drift from the public export and make it look like two implementations are in play. |
| **Sources** | roxom-markets/roxtopia#1198 |
| **Promoted** | no |

### test-names-describe-behavior

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Name tests for the product behavior, not a flag, unit, or leftover condition the change is removing. |
| **Rationale** | Flag- or unit-tied titles go stale when the gate is untangled or the feature becomes unit-agnostic. |
| **Sources** | roxom-markets/roxtopia#1175, roxom-markets/roxtopia#1178 |
| **Promoted** | yes |

### shared-test-config-ports

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Put integration listen ports in the shared test config map, one entry per suite; do not hardcode ports in the spec or collapse suites onto one listen port. |
| **Rationale** | Per-file ports drift, and a single shared port races under parallel workers. |
| **Sources** | roxom-markets/roxtarsverse#823, roxom-markets/roxtarsverse#824, roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### match-sibling-test-location

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Place new integration specs in the same folder as sibling endpoint tests. |
| **Rationale** | A second folder invents a layout the rest of the suite does not use. |
| **Sources** | roxom-markets/roxtarsverse#823 |
| **Promoted** | no |

## Architecture

### no-wire-type-paths

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Do not add dedicated code paths for wire types the upstream contract does not send, even when a broad schema union includes them. |
| **Rationale** | Extra branches for impossible inputs add noise and imply a contract that does not exist on the wire. |
| **Sources** | roxom-markets/roxtopia#833 |
| **Promoted** | no |

### verify-domain-guards

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Do not remove domain-specific guards without verifying multi-phase event flows; a simplified null check may miss intermediate states. |
| **Rationale** | Some domains emit sequential updates where an early message uses a sentinel value before the final state is known. |
| **Sources** | roxom-markets/roxtopia#833 |
| **Promoted** | no |

### no-fallback-unproduced-states

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Do not add display fallbacks for notification or UI states the upstream pipeline never emits, and do not invent default tickers or assets when a lookup is unresolved. |
| **Rationale** | Fallback copy for impossible or unresolved states misleads readers and hides gaps between product intent and actual event contracts. |
| **Sources** | roxom-markets/roxtopia#832, roxom-markets/roxtopia#958 |
| **Promoted** | yes (already in block-reviewer) |

### keep-proto-success-envelopes

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Keep existing proto success-envelope shapes — success plus optional data plus optional error — instead of flattening a single field onto the response. |
| **Rationale** | Flattening a one-field payload breaks the envelope siblings already use and forces callers onto a one-off contract. |
| **Sources** | roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### validate-inbound-ids-at-handler

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Validate inbound ID format at the handler before calling the service, and return the domain invalid-id error instead of letting the database fail. |
| **Rationale** | A bad UUID should be a client error at the API boundary, not a driver exception from the store. |
| **Sources** | roxom-markets/roxtarsverse#823, roxom-markets/roxtarsverse#824, roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### generic-errors-to-callers

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Return a generic internal message to callers for unmapped failures; log the full error only. |
| **Rationale** | Raw database or driver errors leak internals and are not a stable client contract. |
| **Sources** | roxom-markets/roxtarsverse#823, roxom-markets/roxtarsverse#824, roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### db-constraint-matches-service-rule

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | When a service enforces a format rule, add a matching database CHECK constraint and keep the two expressions equal. |
| **Rationale** | A service-only rule lets bad rows in through other writers; a mismatched constraint drifts from the domain. |
| **Sources** | roxom-markets/roxtarsverse#824 |
| **Promoted** | no |

### validate-before-transaction

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Run cheap validation before opening a transaction so invalid requests do not hold connections. |
| **Rationale** | Transactions are scarce; format failures should fail before they occupy a client. |
| **Sources** | roxom-markets/roxtarsverse#824 |
| **Promoted** | no |

### no-transaction-for-single-read

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Do not open a transaction for a single read; use the non-transaction query path siblings already have. |
| **Rationale** | A transaction around one SELECT adds lock and connection cost with no atomicity benefit. |
| **Sources** | roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### skip-empty-table-backfill

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Do not add a data backfill when production and recreate-from-migrations both start empty; add a NOT NULL column in one step. |
| **Rationale** | An UPDATE on an empty table is dead migration surface. |
| **Sources** | roxom-markets/roxtarsverse#824 |
| **Promoted** | no |

### one-handler-per-file

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Put each HTTP or gRPC handler in its own file rather than bundling multiple endpoints together. |
| **Rationale** | One file per endpoint is easier to test, track, and read, and matches the usual handler layout. |
| **Sources** | roxom-markets/window#803 |
| **Promoted** | no |

### map-upstream-errors-to-http

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Map errors at the HTTP boundary: client and validation failures 4xx, faults in this service 5xx, upstream or transport failures 502; do not forward proto codes in the HTTP body. |
| **Rationale** | Forwarded upstream codes leak internal contracts and mix client mistakes with dependency outages. |
| **Sources** | roxom-markets/window#802 |
| **Promoted** | no |

### auth-identity-is-401

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Map upstream rejection of the session identity to 401, not 500. |
| **Rationale** | A rejected session user is an auth failure, the same as a missing session, not an internal error. |
| **Sources** | roxom-markets/window#803 |
| **Promoted** | no |

### one-shared-hook-not-domain-copy

| Field | Value |
|-------|-------|
| **Category** | architecture |
| **Guideline** | Keep shared client hooks in a shared module; do not duplicate them under a domain folder. A compatibility re-export is enough for old import paths. |
| **Rationale** | Domain-copied hooks diverge fetch paths and cache behavior from the rest of the app. |
| **Sources** | roxom-markets/roxtopia#1179 |
| **Promoted** | no |

## Patterns

### avoid-thin-wrappers

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Avoid thin wrapper functions when a simple inline check at the call site is clearer. |
| **Rationale** | Unnecessary wrappers add indirection without improving testability or reuse. |
| **Sources** | roxom-markets/roxtopia#833, roxom-markets/roxtarsverse#824, roxom-markets/window#803 |
| **Promoted** | no |

### avoid-useeffect-derived-state

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Prefer declarative state sync — for example react-hook-form values — over useEffect and ref patterns when resetting form state on open. |
| **Rationale** | Derived state belongs in the render path; effects and refs add imperative complexity and stale-state risk. |
| **Sources** | roxom-markets/roxtopia#841 |
| **Promoted** | no |

### remove-refactor-leftovers

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Remove parameters, wiring, and inline objects left over from an earlier implementation after changing approach. |
| **Rationale** | Leftover API surface confuses reviewers and suggests behavior that no longer exists. |
| **Sources** | roxom-markets/roxtopia#841 |
| **Promoted** | no |

### reuse-existing-state

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Derive remount keys or similar triggers from existing state instead of introducing new state solely for that purpose. |
| **Rationale** | Extra state duplicates information already available and increases synchronization surface. |
| **Sources** | roxom-markets/roxtopia#841 |
| **Promoted** | no |

### extract-nullish-chains

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Extract unclear nullish-coalescing chains into named helpers or earlier variables so precedence and intent are readable. |
| **Rationale** | Inline ?? operators obscure which value wins and why a default exists. |
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

### shared-constants-not-magic

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Replace hardcoded numeric defaults with existing constants from schemas or shared packages. |
| **Rationale** | Shared constants keep defaults consistent across services and make updates single-sourced. |
| **Sources** | roxom-markets/roxtopia#843, roxom-markets/roxtopia#859 |
| **Promoted** | yes (already in block-reviewer) |

### type-appropriate-operations

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Apply operations only on branches where the value type warrants them; do not run string cleanup such as trim on paths where the value is already validated as a non-padded type. |
| **Rationale** | Defensive normalization on the wrong type implies a contract the producer does not guarantee and adds dead code. |
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

### single-return-formatters

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Structure formatter functions with one assignment path and a single return at the end rather than many scattered returns. |
| **Rationale** | A single exit makes the full transformation visible and easier to follow. |
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

### remove-redundant-type-checks

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Remove redundant typeof branches when a single coercion handles all cases equivalently. |
| **Rationale** | Extra type checks suggest false distinctions and clutter the main path. |
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

### extract-named-predicates

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Extract multi-condition domain checks into named helpers when inline OR or AND chains obscure intent. |
| **Rationale** | Named predicates document the domain question being asked and keep call sites readable. |
| **Sources** | roxom-markets/roxtopia#859 |
| **Promoted** | no |

### no-forced-shared-helpers

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Do not force a shared helper across similar paths when contracts, return shapes, or domain branches diverge enough that sharing adds indirection without gain. |
| **Rationale** | Forced reuse can obscure differences that callers rely on and inflate the shared API for little benefit. |
| **Sources** | roxom-markets/roxtopia#859, roxom-markets/roxtopia#1178 |
| **Promoted** | no |

### match-sibling-ui-patterns

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | When fixing UI layout or scroll behavior, match the working pattern from sibling components in the same feature before inventing a new approach. |
| **Rationale** | Sibling patterns already encode viewport and chrome constraints that ad-hoc fixes miss. |
| **Sources** | roxom-markets/roxtopia#956, roxom-markets/roxtopia#1183 |
| **Promoted** | no |

### extend-via-optional-props

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Prefer optional props on the shared underlying component over an extra wrapper when only layout or styling differs for one caller. |
| **Rationale** | Extra wrappers add nesting noise and risk breaking other call sites less cleanly than an opt-in prop. |
| **Sources** | roxom-markets/roxtopia#956 |
| **Promoted** | no |

### suppress-unresolved-display

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | When a catalog or lookup race leaves a value unresolved, return the raw value from the resolver and suppress raw ID display at call sites until resolved instead of inventing empty sentinels in the resolver. |
| **Rationale** | Empty returns hide mixed publisher shapes, while call-site suppression handles loading without showing UUIDs as labels. |
| **Sources** | roxom-markets/roxtopia#958 |
| **Promoted** | no |

### match-sibling-route-registration

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Register routes, middleware, and handlers using the same shape as siblings in the file; only add extra middleware or wrappers when this endpoint actually needs them. |
| **Rationale** | Handler-exported path constants and one-off wrappers invent a second registration style the rest of the router does not use. |
| **Sources** | roxom-markets/window#801, roxom-markets/window#802 |
| **Promoted** | no |

### match-generated-client-calls

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Do not attach tracing or extra metadata to generated client calls that sibling handlers do not pass; match the generated client's actual signature. |
| **Rationale** | Invented metadata implies a tracing contract the generated client does not support. |
| **Sources** | roxom-markets/window#800 |
| **Promoted** | no |

### no-custom-uuid-guards

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Do not add custom UUID regex or extra type-safety helpers when the database column or existing shared mappers already constrain the type. |
| **Rationale** | Reinvented UUID checks duplicate constraints the store already enforces and add processing on every row. |
| **Sources** | roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### validate-from-handlers-not-effects

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Prefer triggering validation from event handlers rather than effects; keep an effect only when a derived value updates without firing those handlers. |
| **Rationale** | Handler-driven validation matches the user event; an effect is justified when a quote or other derived amount never fires onChange. |
| **Sources** | roxom-markets/roxtopia#1074 |
| **Promoted** | no |

### single-use-vendor-error-codes

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | When detecting a vendor SQLSTATE the library does not export, hardcode it at the single use site with a comment to the vendor docs; do not invent a shared constant unless a sibling already names that same code. |
| **Rationale** | A one-off named constant for a code used once implies a shared catalog that does not exist; the comment is what makes the magic string reviewable. |
| **Sources** | roxom-markets/roxtarsverse#824 |
| **Promoted** | no |

### consume-original-shared-exports

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Consume the original shared export for canonical lists, constants, and endpoint paths; do not duplicate a local array, path string, or renaming re-export. |
| **Rationale** | Local copies and aliases drift when items are added, removed, or sorted. |
| **Sources** | roxom-markets/roxtopia#1179, roxom-markets/roxtopia#1231 |
| **Promoted** | no |

### shared-error-constants

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Map errors with shared constants or typed errors on both sides; do not compare free-form error strings. |
| **Rationale** | A typo in a string comparison silently maps to the wrong client code. |
| **Sources** | roxom-markets/roxtarsverse#824 |
| **Promoted** | no |

### reproducible-codegen-config

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Fix the generator config so clients are reproducible; do not hand-write generated files. |
| **Rationale** | Hand-edited generated output diverges from the next generate run. |
| **Sources** | roxom-markets/roxtarsverse#823, roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### dispatch-by-sent-field

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Resolve lookups from the field the caller sent; do not sniff UUID shape or add a path that echoes IDs back unchanged. |
| **Rationale** | Shape-sniffing treats invalid IDs as symbols and identity passthrough hides whether a lookup occurred. |
| **Sources** | roxom-markets/window#803 |
| **Promoted** | no |

### derive-http-types-from-domain

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Derive HTTP projections from the domain type instead of restating a parallel interface for the same entity. |
| **Rationale** | Parallel types drift and reviewers cannot tell which shape is canonical. |
| **Sources** | roxom-markets/window#803 |
| **Promoted** | no |

### no-empty-string-as-undefined

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Do not coerce empty string to undefined via truthiness; validate required fields before the helper, and treat only undefined as omitted. |
| **Rationale** | Truthy defaults hide invalid empty input and change the helper's contract. |
| **Sources** | roxom-markets/window#803 |
| **Promoted** | no |

### keep-canonical-separate-from-display

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Keep the canonical stored or original value separate from display formatting; do not persist masks, derive originals from painted strings, or treat formatted output as the source of truth. |
| **Rationale** | Display formatting is a read-path concern; storing or reversing it corrupts the contract. |
| **Sources** | roxom-markets/roxtarsverse#824, roxom-markets/roxtopia#1194 |
| **Promoted** | no |

### colocate-handler-schemas

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Put request schemas in a sibling schema file next to the handler, matching existing handler-dir patterns. |
| **Rationale** | Inline schemas clutter the handler and diverge from how other endpoints colocate validation. |
| **Sources** | roxom-markets/window#802 |
| **Promoted** | no |

### single-loading-skeleton

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Do not add a second skeleton for a dependent field; hide it until the existing load finishes. |
| **Rationale** | Extra skeletons imply a separate wait and duplicate loading chrome. |
| **Sources** | roxom-markets/roxtopia#1178 |
| **Promoted** | no |

### use-decimal-helpers

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Use shared decimal helpers for money and FX math; do not use native number division. |
| **Rationale** | Native division loses precision that decimal.js helpers already encapsulate. |
| **Sources** | roxom-markets/roxtopia#1183 |
| **Promoted** | no |

### log-presence-not-secrets

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Log whether a secret exists, never the secret itself. |
| **Rationale** | Presence flags are enough for diagnostics; logging the value leaks it. |
| **Sources** | roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

### no-redundant-membership-guards

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Do not re-check list membership for values already produced from that list; keep only the type guard the callback's declared type requires. |
| **Rationale** | Extra includes checks imply the mapped items are untrusted and duplicate the source list. |
| **Sources** | roxom-markets/roxtopia#1162 |
| **Promoted** | no |

## Style

### precise-docstrings

| Field | Value |
|-------|-------|
| **Category** | style |
| **Guideline** | Use precise domain terms in docstrings — name the producing service and data shape — instead of vague labels. |
| **Rationale** | Vague terminology forces readers to guess which layer and format the code handles. |
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

### helper-docstrings

| Field | Value |
|-------|-------|
| **Category** | style |
| **Guideline** | Add what-and-why docstrings on helpers and public components whose purpose or variant options are not obvious from the name alone. |
| **Rationale** | Non-obvious helpers and variant APIs need context about the contract they expose, not just a restatement of the name. |
| **Sources** | roxom-markets/roxtopia#843, roxom-markets/roxtopia#1162 |
| **Promoted** | no |

### comment-regex-patterns

| Field | Value |
|-------|-------|
| **Category** | style |
| **Guideline** | Add a brief comment on each regex explaining what it matches and which contract it enforces. |
| **Rationale** | Regex intent is not self-documenting; a one-line note prevents misreading allowed shapes. |
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

### prefer-design-tokens

| Field | Value |
|-------|-------|
| **Category** | style |
| **Guideline** | Prefer existing design-system tokens for color, spacing, and typography over arbitrary Tailwind values; keep an arbitrary value only when no close token exists and note why. |
| **Rationale** | Arbitrary utilities drift from the design system and make later theme changes harder. |
| **Sources** | roxom-markets/roxtopia#874 |
| **Promoted** | no |

## Performance

### sql-alias-instead-of-row-map

| Field | Value |
|-------|-------|
| **Category** | performance |
| **Guideline** | Alias SQL columns to application field names in the query instead of transforming rows in application code after fetch. |
| **Rationale** | Post-fetch mappers add a pass over every row that the query can avoid with column aliases. |
| **Sources** | roxom-markets/roxtarsverse#825 |
| **Promoted** | no |

## Other

_(none yet)_
