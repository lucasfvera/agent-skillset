---
id: 20260727T203702Z-roxom-markets-roxtopia-pr958
status: pending
capturedAt: 2026-07-27T20:37:02Z
actionedAt: null
pr: roxom-markets/roxtopia#958
prUrl: https://github.com/roxom-markets/roxtopia/pull/958
fixCommitSha: 3dbbf1558f69326d957974dfe5e3b6bd3b6782fd
threadCount: 2
---

# Session capture — roxom-markets/roxtopia#958

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6S-5S0 |
| **path** | packages/shared/src/header/notification-center/helpers.ts |
| **line** | 369 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/notification-center/helpers.ts, packages/shared/src/header/notification-center/helpers.test.ts, packages/shared/src/header/notification-center/normalizeNotificationMessages.test.ts |

### Reviewer comment

Why do we assume that if the ticker is unresolved, we should return USDT?

### Resolution

Valid. Inventing `USDT` for an unresolved principal id was the wrong fallback. We now omit the ticker until the catalog resolves (amount still uses the existing principal decimals scale). Collateral still defaults to BTC as a product assumption.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | review:4748640322 |
| **path** | — |
| **line** | — |
| **verdict** | dismissed |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

I think the issue is related to loading times right? It seems that until we find the instrument, it resolves as undefined and we show the instrumentId.

### Resolution

Dismissed. Already covered in prior follow-up comment with marker `<!-- bmo-review-followup:4748640322 -->`.
