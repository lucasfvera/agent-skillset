# Block reviewer learnings catalog

Abstract guidelines distilled from PR review session captures in `inbox/`. **Do not paste verbatim comments here.**

Pending captures live in [inbox/pending/](../inbox/pending/). Processed captures move to [inbox/actioned/](../inbox/actioned/). Run [`bmo-update-block-reviewer-skill`](../SKILL.md) to merge pending feedback into this catalog.

The block reviewer skill stays short. See [promotion rules](../references/promotion-rules.md) for what moves into `bmo-block-reviewer/SKILL.md`.

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
| **Sources** | roxom-markets/door#218, roxom-markets/roxtarsverse#751 |
| **Promoted** | yes |

### test-typed-stubs

| Field | Value |
|-------|-------|
| **Category** | typing |
| **Guideline** | Prefer explicit typed no-op stubs over never or unknown shortcuts in test harnesses. |
| **Rationale** | never and unknown hide missing dependency shapes and diverge from how other tests stub the same surface. |
| **Sources** | roxom-markets/roxtarsverse#751 |
| **Promoted** | no |

## Tests

### test-realistic-fixtures

| Field | Value |
|-------|-------|
| **Category** | tests |
| **Guideline** | Use realistic fixture values — UUID v4 for ID fields, real enum members, plausible amounts — not placeholder strings like tx-123 or user-1. |
| **Rationale** | Realistic fixtures mirror production data shapes and catch type or format assumptions early. |
| **Sources** | roxom-markets/roxtopia#833, roxom-markets/roxtopia#832 |
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
| **Guideline** | Reuse shared suite mocks for common dependencies instead of inventing one-off mock shapes in a single spec. |
| **Rationale** | Shared mocks keep harness behavior consistent and avoid drift from the suite baseline. |
| **Sources** | roxom-markets/roxtarsverse#751 |
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
| **Promoted** | yes |

## Patterns

### avoid-thin-wrappers

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | Avoid thin wrapper functions when a simple inline check at the call site is clearer. |
| **Rationale** | Unnecessary wrappers add indirection without improving testability or reuse. |
| **Sources** | roxom-markets/roxtopia#833 |
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
| **Promoted** | yes |

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
| **Sources** | roxom-markets/roxtopia#859 |
| **Promoted** | no |

### match-sibling-ui-patterns

| Field | Value |
|-------|-------|
| **Category** | patterns |
| **Guideline** | When fixing UI layout or scroll behavior, match the working pattern from sibling components in the same feature before inventing a new approach. |
| **Rationale** | Sibling patterns already encode viewport and chrome constraints that ad-hoc fixes miss. |
| **Sources** | roxom-markets/roxtopia#956 |
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
| **Guideline** | Add what-and-why docstrings on helpers whose purpose is not obvious from the name alone. |
| **Rationale** | Non-obvious helpers need context about the data contract they bridge, not just a restatement of the function name. |
| **Sources** | roxom-markets/roxtopia#843 |
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

_(none yet)_

## Other

_(none yet)_
