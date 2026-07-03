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
| **Sources** | roxom-markets/roxtopia#833, roxom-markets/roxtopia#841, roxom-markets/roxtopia#843 |
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
| **Sources** | roxom-markets/door#218 |
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
| **Guideline** | Do not add display fallbacks for notification or UI states the upstream pipeline never emits. |
| **Rationale** | Fallback copy for impossible states misleads readers and hides gaps between product intent and actual event contracts. |
| **Sources** | roxom-markets/roxtopia#832 |
| **Promoted** | no |

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
| **Sources** | roxom-markets/roxtopia#843 |
| **Promoted** | no |

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

## Performance

_(none yet)_

## Other

_(none yet)_
