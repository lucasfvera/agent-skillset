---
name: bmo-step-planner
description: Authors a sliced markdown implementation plan with U1/U2+ units, narrow verification, rollback seams, and review handoff hints.
disable-model-invocation: true
---

# Step-planner (bmo)

This skill defines how to **author a plan** that matches **bmo-step-deliver**: each unit is **easy to review**, **easy to validate**, and **easy to roll back**. It does **not** implement code—only the plan artifact and, if needed, clarifying questions.

## When to use

- Work is **multi-step**, **cross-layer**, or **cross-repo**.
- The user wants **U1 / U2 / …** pacing with explicit **continue** boundaries later.
- Scope is still fuzzy: planning **reduces** invention of defaults (unanswered items stay **blocked**).

## Output location

Write a **single markdown plan file**:

1. **Prefer** `<git-workspace-root>/.plans/<name>.plan.md` when the change primarily lands in one checked-out repository that should own the plan (reuse an existing repo plan directory such as `docs/plans/` if the project already stores plans there).
2. Otherwise use `~/.agents/plans/<name>.plan.md` (e.g. multi-root workspace or repo-agnostic work).

If both are plausible, **ask one forced-choice question** before writing.

**Filename:** `kebab-case-topic` plus optional short disambiguator (e.g. `order-webhook-retry_a1b2c3d4.plan.md`). Avoid overwriting an existing file unless the user asked to revise it; prefer a new filename or a **Revision** section inside the same file if they asked to update in place.

## Hard rules

1. **Planning only** — no implementation, no drive-by refactors, no “quick fix” patches in this mode.
2. **Mandatory units (`U1`, `U2`, …) & stacked PR default** — every plan with more than one delivery step must use **`U1`, `U2`, …`** (in order). Each unit is one **natural pause** for `bmo-step-deliver` and maps to **one stacked PR** by default when built via `bmo-builder`.
3. **Vertical slicing & ~100–200 LOC production budget** — scope each **`U*`** as a **self-contained, significant vertical slice** (or a single domain prerequisite such as a schema/migration when ordering requires it) targeting **~100 LOC of production code (soft ceiling ~200 LOC, excluding tests, lockfiles, snapshots, and generated code)**.
4. **Keep tests in the same unit/PR** — every `U*` must include the unit/integration tests that prove its behavior. **Never split tests into a separate unit or separate PR** to stay under the LOC ceiling; each PR must be meaningful and verifiable on its own.
5. **No invented defaults** — if a decision matters and is unknown, list it under **Open questions (blocked)** with a forced-choice line or require an explicit token such as `defaults: yes` before any dependent slice is treated as decided (same spirit as bmo-step-deliver).
6. **Coherent checkpoints** — after each unit, the tree must remain **shippable**: build and tests for touched packages pass on that slice alone.

## Plan template (copy into the file)

Use this structure; keep prose tight.

```markdown
# <Title>

## Goal
<one paragraph>

## Non-goals
- …

## Context
- Repos / packages involved:
- Contracts & backing docs (specs, ADRs, schemas, queues, flags):

## Open questions (blocked)
- … (if none, write **None**)

## Dependencies & order
- e.g. schema prerequisite in U1 before vertical feature slices in U2/U3 — **or** “none”

## Implementation units

### U1 — <short name (Part 1 of k)>
- **Scope in (vertical slice + tests):** …
- **Scope out:** …
- **Estimated production LOC:** ~<N> LOC (excluding tests/codegen/locks; ≤200 LOC soft ceiling)
- **Likely touchpoints (tentative):** paths or packages
- **Decisions & backing docs:** key trade-offs/assumptions and the spec, schema, or sibling file backing them
- **Failure modes & boundary risks:** contracts, status mappings, transactions, or race states for human review
- **Verification (narrowest):** commands or checks (e.g. `yarn --cwd "<abs>" test path/to.spec.ts`)
- **Rollback seam:** what to revert / feature flag / deploy note

### U2 — <short name (Part 2 of k)>
…

## After planning
Attach **bmo-step-deliver** for execution (or run via **bmo-builder** for stacked PR delivery). One **U*** per assistant turn unless the user opts into single-pass.
```

## Quality bar

- Each **U*** maps to **one significant, reviewable vertical slice (with its tests)** under the ~200 LOC production-code soft ceiling, never “misc fixes” or a test-only follow-up PR.
- Verification lines must respect **correct workspace** (prefer `yarn --cwd "<absolute-path>"` in multi-root setups).
- Call out **multi-git-root** work: which unit belongs to which repo and that **commits need explicit approval per repo** during manual delivery.

## Relationship to bmo-step-deliver

- **This skill** → produces the **plan file** and **U*** boundaries.
- **bmo-step-deliver** → executes **one U*** per turn with handoff + verify + pause.

Do not duplicate the full delivery checklist here; reference it at execution time.
