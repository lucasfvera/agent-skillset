# Extraction rules — PR feedback to guidelines

## Goal

Produce **durable review rules** a future `bmo-block-reviewer` pass can apply without re-reading the original thread.

## Abstraction ladder

| Thread content | Extract as |
|----------------|------------|
| "Use `===` here" | Enforce strict equality in comparisons |
| "Extract this to a helper" | Extract reusable logic when it improves testability or removes duplication |
| "This test should use getByRole" | Prefer accessible queries (`getByRole`) over `getByTestId` when a role exists |
| "Why is this guard here?" | Avoid defensive checks for states that cannot occur in this path |
| "Rename to match sibling file" | Match established patterns in sibling files before inventing new structure |
| "Nit: extra blank line" | **Skip** — too local; not a catalog learning |
| "Fix the typo in the comment" | **Skip** unless it reveals a standing doc rule |

## Rules

1. **Source is inbox captures**, not live GitHub, unless recovery fetch is needed.
2. **One thread → zero or one learning.** Multiple distinct rules in one comment → split into separate learnings with different `id`s.
3. **Imperative voice.** "Prefer X over Y when Z" not "Reviewer wanted X".
4. **No quotes in catalog.** Inbox captures may hold verbatim comments; `guideline` and `rationale` in the catalog must not paste them.
5. **No paths in guidelines.** `sources` holds `owner/repo#number` for traceability only.
6. **Resolution informs rationale, not wording.** A `Keeping as-is` thread can still yield a learning ("Do not add guards for X because Y") when it encodes a standing preference.
7. **Dismissed nitpicks:** extract only when the dismissal explains a **repeatable** bar (e.g. "we don't enforce import order in test files").
8. **Cross-session dedupe:** the same abstract rule from multiple pending captures merges into one learning with combined `sources`.

## Category guide

| Category | Examples |
|----------|----------|
| `typing` | `any`, assertions, strict equality, branded IDs |
| `tests` | query priority, user-event, fixtures, mock boundaries |
| `architecture` | layer boundaries, handler vs service, file placement |
| `patterns` | reuse helpers, DRY, colocation, sibling-file consistency |
| `style` | naming, comments worth keeping, magic strings |
| `performance` | latency on hot paths, unnecessary awaits |
| `other` | anything that does not fit above |

## Examples

### Thread

> Reviewer: "Please use strict equality"
> Resolution: Valid. Replaced `==` with `===`.

### Learning

```yaml
id: strict-equality
category: typing
guideline: Always use strict equality when comparing values.
rationale: Loose equality hides type coercion bugs.
sources: [roxom-markets/roxtopia#833]
promoted: false
```

### Thread

> Reviewer: "Can we use getByRole here? The button has a name."
> Resolution: Valid. Updated query.

### Learning

```yaml
id: test-accessible-queries
category: tests
guideline: Prefer getByRole (and other accessible queries) before getByTestId when the element exposes role and name.
rationale: Tests should reflect how users find elements and catch accessibility regressions.
sources: [roxom-markets/roxtopia#833]
promoted: false
```

### Thread (dismissed)

> Reviewer: "Add a try/catch around this internal mapper call."
> Resolution: Keeping as-is. Mapper is pure; callers own error boundaries.

### Learning

```yaml
id: no-defensive-internal-wrap
category: patterns
guideline: Do not wrap pure internal helpers in try/catch; handle errors at the boundary that owns I/O or user-facing failure.
rationale: Extra catches obscure the real failure site and duplicate handling.
sources: [roxom-markets/roxtarsverse#120]
promoted: false
```

## When to skip

- One-off factual corrections ("wrong enum value for this constant").
- Typos, formatting-only requests, or single-use naming preferences.
- Feedback that only applies to one unreleased feature flag state.
- Duplicates of an existing catalog entry (merge sources instead).
