---
id: 20260821T124310Z-roxom-markets-roxtarsverse-pr825
status: actioned
capturedAt: 2026-08-21T12:43:10Z
actionedAt: 2026-08-25T02:59:47Z
pr: roxom-markets/roxtarsverse#825
prUrl: https://github.com/roxom-markets/roxtarsverse/pull/825
fixCommitSha: 809d4aa0b1e73e373c6937b45cd21c14e2c1dadd
threadCount: 2
---

# Session capture — roxom-markets/roxtarsverse#825

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOObcV4c6bJkpi |
| **path** | apps/roxtars/src/infrastructure/repository/antiPhishingCodesRepository.ts |
| **line** | 35 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | apps/roxtars/src/infrastructure/repository/antiPhishingCodesRepository.ts, apps/roxtars/src/infrastructure/sql/antiPhishingCodes.ts |

### Reviewer comment

We can avoid using this method by using the "as" directly in the sql query. This way we avoid extra processing. This method is underperformant and should not be used.

### Resolution

Valid. Dropped `mapSnakeToCamel` and aliased camelCase columns in the SQL so the row can be returned as-is.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOObcV4c6bJ1T5 |
| **path** | apps/roxtars/tests/integration/grpc/users/getAntiPhishingCode.integration.test.ts |
| **line** | 70 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | apps/roxtars/tests/integration/grpc/users/getAntiPhishingCode.integration.test.ts |

### Reviewer comment

Why are you wrapping the call in a promise? The handler already returns a promise. Can't we just call the client and await? I think we do that in other tests. And also I think that's how we will use it.

### Resolution

Valid. The generated client is callback-only, so we promisify it once and `await getAntiPhishingCode({ userId })` in each case.
