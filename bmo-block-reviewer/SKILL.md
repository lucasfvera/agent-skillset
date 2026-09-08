---
name: bmo-block-reviewer
description: Findings-first review of a code diff against BMO quality rules and the team learnings catalog.
disable-model-invocation: true
---

# Block reviewer (bmo)

Review the changed files the way the user reviews them: short, practical, biased toward code quality that fits their style.

This skill covers a delivery-digest block, a PR-fix slice, or any named diff. Parent skills (`bmo-builder`, `bmo-respond-pr-review`) spawn reviewers; they own orchestration.

## Default evidence

1. Prefer the actual changed files and diff.
2. Use handoff text (block digest, verification notes, review comment) as supporting context.
3. If the diff is unavailable, review the handoff text only and say the review is limited by missing code context.

## Scope

Review only the files in this handoff. When a digest is present, treat its **Review:** bullets as acceptance criteria. Work deferred to a later unit is **Deferred (out of scope)**, not a blocker. Cite a sibling file when flagging pattern drift.

## What to look for

- Incorrect typing. Never allow `any`.
- Type with the real contract; skip `as` unless there is no cleaner option. Do not cast queried elements when the locator already provides the type.
- Type test fixtures with the producing service's contract types, not loose object shapes.
- Preserve comments that help the next person understand the code.
- Skip over-defensive checks for states that cannot happen on this path.
- Extract reusable logic into its own file when that makes testing easier.
- Check for duplication before accepting new code. Reuse shared suite mocks for common dependencies instead of one-off mock shapes.
- Code that changes together should stay close together.
- Flag added latency on the hot path of the changed code.
- Always use strict equality when comparing values.
- Replace hardcoded numeric defaults with existing constants from schemas or shared packages.
- Skip display fallbacks for notification or UI states the upstream pipeline never emits. Do not invent default tickers or assets when a lookup is unresolved.

## When reviewing tests

- Prefer queries from more accessible to less accessible: `getByRole` first, `getByTestId` last.
- Prefer behavior from the user perspective, not implementation details.
- Keep queries separate from assertions for readability. Assign `screen.getBy...` results to variables first.
- Use `user-event` when interaction matters. Use `fireEvent` only when user-event cannot drive the case.
- Avoid magic strings. If a repeated string is needed, extract it to a well-named `SCREAMING_SNAKE_CASE` constant in the same test file.
- Avoid comments that do not add value. Test code should mostly explain itself.
- Do not assert on mocked component behavior that the mock itself defines. Assert that the mocked component is rendered when needed, usually through a test id.
- If a mocked child receives a transformed value from the real logic under test, asserting that transformed value is acceptable.
- Fixture values should be as close as possible to real data: UUID v4, real enum members, plausible amounts, not `'tx-123'` or `'user-1'`.
- Integration tests should use the shared suite factory and call the generated client the way production does; do not invoke handlers directly or wrap them in test-only helpers.
- Do not assert negatives for product or timeline choices, route constants, or other details that are not a hard contract.
- Do not re-test behavior owned by another method or already covered in a related change; keep the spec scoped to the code under review.

## Accumulated learnings

Read [`learnings/catalog.md`](learnings/catalog.md) before a ship verdict. Apply every catalog guideline whose category matches this diff (test files → tests; types/schemas → typing; and so on). Scan remaining categories when the change could hit them. The whole catalog binds, not only **Promoted: yes** rows.

**Done:** every matching catalog guideline is a finding or explicitly N/A on the Catalog line. A ship verdict without that read is incomplete.

## What not to do

Stay on this diff's quality bar (typing, tests, duplication, catalog). Skip generic security hunts, invented edge cases, style nits when the block is sound, and praise or long summaries.

## Output

Keep the response short and findings-first.

Use this shape:

```markdown
<highest-signal findings first, one bullet each>

Catalog: <matching catalog ids applied or N/A, one line>

What is fine:
- <brief note only if worth saying>

Verdict: <short verdict>
```

**Done:** output matches this shape; the Catalog line is present; Verdict is not ship unless Catalog is filled.

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
