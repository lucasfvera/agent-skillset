---
name: bmo-block-reviewer
description: Reviews a delivered execution block using a specific BMO-style lens instead of a generic defensive code review. Prefer inspecting the actual diff and changed files; use the delivered block text as supporting context. Use when the user says /bmo-block-reviewer, asks to review a block from bmo-step-deliver, wants a short findings-first review of a delivery slice, or when a parent agent spawns one reviewer per digest block.
disable-model-invocation: true
---

# Block reviewer (bmo)

Review the delivered block the way the user reviews it: short, practical, and biased toward code quality that fits their style.

## Default evidence

1. Prefer the actual changed files and diff.
2. Use the delivered block text, verification notes, and review digest as supporting context.
3. If the diff is unavailable, review the handoff text only and say that the review is limited by missing code context.

## Multi-block orchestration

When the user asks to review **each block** from a `bmo-step-deliver` digest:

**Parent agent**

1. Deliver the slice (implement → verify → review digest) before spawning reviewers.
2. Spawn **one subagent per block** (`Block A`, `Block B`, …). Wait for all to finish.
3. Triage each finding: **real** (fix), **style** (fix only when a clear repo/sibling pattern or prior user feedback applies), **deferred** (intentional slice boundary — do not fix).
4. Fix only **real** issues, rerun the same narrow verification from the handoff, then summarize.

**Pass each subagent:** the block text (including **What to review** and per-file **Review:** bullets), slice `Scope`, plan non-goals, changed file paths, `git diff` for those paths, one sibling file to compare against (e.g. existing deposit publisher), and what verification already passed.

**Subagent rules:** review only this block’s files; treat the block’s **Review:** bullets as acceptance criteria; flag missing work deferred to a later unit under **Deferred (out of scope)** instead of as a blocker; cite the comparison file when flagging pattern drift.

**Parent summary (short):** per block — real / style / deferred — then **Fixing now** vs **Not fixing** with one-line reasons.

## What to look for

- Incorrect typing. Never allow `any`.
- Avoid `as` type assertions unless there is no cleaner option.
- Preserve comments that help the next person understand the code.
- Do not reward over-defensive checks for unrealistic scenarios.
- Prefer extracting reusable logic into its own file when that makes testing easier.
- Look for helper functions that could be extracted into another file for clarity.
- Check for duplication before accepting new code.
- Code that changes together should stay close together.
- Be mindful about if the introduced code adds latency to the original code.
- Always use strict equality when comparing values.

## When reviewing tests

- Prefer queries from more accessible to less accessible: `getByRole` first, `getByTestId` last.
- Prefer behavior from the user perspective, not implementation details.
- Keep queries separate from assertions for readability. Assign `screen.getBy...` results to variables first.
- Use `user-event` when interaction matters. Avoid `fireEvent` unless there is a clear reason.
- Avoid magic strings. If a repeated string is needed, extract it to a well-named `SCREAMING_SNAKE_CASE` constant in the same test file.
- Avoid comments that do not add value. Test code should mostly explain itself.
- Do not assert on mocked component behavior that the mock itself defines. Instead, assert that the mocked component is rendered when needed, usually through a test id.
- If a mocked child receives a transformed value from the real logic under test, asserting that transformed value is acceptable.
- Fixture values should be as close as possible to real data: UUID v4, real enum members, plausible amounts—not `'tx-123'`, `'user-1'`.

## Accumulated learnings

Team-specific rules distilled from PR review live in
[`bmo-update-block-reviewer-skill/learnings/catalog.md`](../bmo-update-block-reviewer-skill/learnings/catalog.md).
Apply them when they strengthen or specialize the rules above.

## What not to do

- Do not turn this into a generic security or edge-case hunt.
- Do not invent unlikely failure scenarios just to sound thorough.
- Do not nitpick style when the block is sound.
- Do not flood the review with praise or long summaries.

## Output

Keep the response short and findings-first.

Use this shape:

```markdown
<highest-signal findings first, one bullet each>

What is fine:
- <brief note only if worth saying>

Verdict: <short verdict>
```

## Finding style

Each finding should say:

1. what is wrong,
2. why it matters in this codebase,
3. what to change.

Prefer concrete wording like:

- `Uses \`any\` in a new path. Type this explicitly so the caller contract stays checkable. Replace it with <expected type>.`
- `This guard is too defensive for a state that cannot happen here. Remove it and keep the main path direct.`
- `This logic duplicates the mapper already present in <path>. Reuse that helper instead of adding a second copy.`
- `This test reaches for \`getByTestId\` even though the element has a role and accessible name. Query it the way the user experiences it.`
- `This assertion checks the mocked component output instead of the behavior under test. Assert the transformed prop or the presence of the mock, not what the mock was hardcoded to render.`

## If the block is good

Say so plainly. Mention only the one or two things that are notably solid, then give a short verdict.
