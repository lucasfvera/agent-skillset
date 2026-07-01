---
id: 20260627T003050Z-roxom-markets-roxtopia-pr832
status: pending
capturedAt: 2026-06-27T00:30:50Z
actionedAt: null
pr: roxom-markets/roxtopia#832
prUrl: https://github.com/roxom-markets/roxtopia/pull/832
fixCommitSha: f4d8778110771f6349e94ee81bb680eed8ac99eb
threadCount: 2
sourceTranscript: d7b13d60-0244-4c8b-9174-ad92bca6841f
backfillNote: Backfilled from agent transcript + GitHub resolved threads (pre-inbox capture).
---

# Session capture — roxom-markets/roxtopia#832

Backfilled from agent transcript + GitHub resolved threads (pre-inbox capture).

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6MqUg_ |
| **path** | `packages/shared/src/header/notification-center/normalizeNotificationMessages.ts` |
| **line** | — |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Why would we show fallbacks when the internal transaction is not completed? Shouldn't we have a pending state? Is there pending internal transaction as we have for on chain deposits/withdrawals?

### Resolution

Valid. Tx only publishes completed internal transfers to Hermod (`shouldSendHermodInternalTransferNotification`), so there is no pending notification state today. Removed the non-completed status fallback and kept generic copy only when the instrument catalog cannot resolve `instrumentId`.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6MqUvA |
| **path** | `packages/ws/src/__tests__/notifications.router.test.ts` |
| **line** | 1 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Use real uuids where needed.

### Resolution

Valid. Replaced placeholder ids and channel names in the internal-transfer fixtures with canonical UUIDs and `notifications:<userId>`.
