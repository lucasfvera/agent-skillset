---
id: 20260907T175939Z-roxom-markets-roxtopia-pr1198
status: actioned
capturedAt: 2026-09-07T17:59:39Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1198
prUrl: https://github.com/roxom-markets/roxtopia/pull/1198
fixCommitSha: 5e188ac9c69ed78d0b7aca3bb70e7983034dffdf
threadCount: 1
---

# Session capture — roxom-markets/roxtopia#1198

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | review:5134435332 |
| **path** | — |
| **line** | — |
| **verdict** | partially_valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/portfolio/components/Finance/TransformedPrice/TransformedPrice.test.tsx |

### Reviewer comment

Why do we have 2 TransformedPrice tests? Do we also have the component duplicated? Does it make sense to refactor it and keep a single one? Or do we have 2 for some reason?

### Resolution

Partially valid. Yes — `TransformedPrice` (and the futures tables) exist twice: the live copy under `src/components` that `@roxtopia/shared/portfolio/*` actually exports, and an unused leftover lift under `src/portfolio`. Collapsing those trees is a separate migration and should not ride this bugfix.

The extra test covered only the unused copy. Removed it in `5e188ac9c`; the live `src/components` spec stays.
