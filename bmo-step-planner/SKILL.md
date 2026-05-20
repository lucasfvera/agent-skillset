---
name: bmo-step-planner
description: Produces an implementation plan as markdown under .cursor/plans with mandatory U1/U2+ units, per-slice verification, rollback seams, and review prompts so later execution can follow bmo-step-deliver. Use when the user invokes /bmo-step-planner, asks for a sliced plan before coding, or has a large or cross-cutting task that needs reviewable units and clear pause boundaries.
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

1. **Prefer** `<git-workspace-root>/.cursor/plans/<name>.plan.md` when the change primarily lands in one checked-out repository that should own the plan.
2. Otherwise use `~/.cursor/plans/<name>.plan.md` (e.g. multi-root workspace or repo-agnostic work).

If both are plausible, **ask one forced-choice question** before writing.

**Filename:** `kebab-case-topic` plus optional short disambiguator (e.g. `kyc-hermod-notify_a1b2c3d4.plan.md`). Avoid overwriting an existing file unless the user asked to revise it; prefer a new filename or a **Revision** section inside the same file if they asked to update in place.

## Hard rules

1. **Planning only** — no implementation, no drive-by refactors, no “quick fix” patches in this mode.
2. **Mandatory units** — every plan with more than one delivery step must use **`U1`, `U2`, …`** (in order). Each unit is one **natural pause** for `bmo-step-deliver` (one user message / **continue** per unit during execution).
3. **No invented defaults** — if a decision matters and is unknown, list it under **Open questions (blocked)** with a forced-choice line or require an explicit token such as `defaults: yes` before any dependent slice is treated as decided (same spirit as bmo-step-deliver).
4. **Coherent checkpoints** — after each unit, the tree should remain **shippable** where possible: build/tests for touched packages still make sense; avoid “half a migration” without an explicit note.

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
- Contracts (APIs, schemas, queues, flags):

## Open questions (blocked)
- … (if none, write **None**)

## Dependencies & order
- e.g. schema before consumers; flag before rollout — **or** “none”

## Implementation units

### U1 — <short name>
- **Scope in:** …
- **Scope out:** …
- **Likely touchpoints (tentative):** paths or packages
- **Verification (narrowest):** commands or checks (e.g. `yarn --cwd "<abs>" test path/to.spec.ts`)
- **Rollback seam:** what to revert / feature flag / deploy note
- **Review handoff hints:** intent, contracts, failure modes (per-file prompts where useful)

### U2 — <short name>
…

## After planning
Attach **bmo-step-deliver** for execution. One **U*** per assistant turn unless the user opts into single-pass there.
```

## Quality bar

- Each **U*** should map to **one reviewable diff** (or one clearly named concern), not “misc fixes.”
- Verification lines must respect **correct workspace** (prefer `yarn --cwd "<absolute-path>"` in multi-root setups).
- Call out **multi-git-root** work: which unit belongs to which repo and that **commits need explicit approval per repo** during delivery.

## Relationship to bmo-step-deliver

- **This skill** → produces the **plan file** and **U*** boundaries.
- **bmo-step-deliver** → executes **one U*** per turn with handoff + verify + pause.

Do not duplicate the full delivery checklist here; reference it at execution time.
