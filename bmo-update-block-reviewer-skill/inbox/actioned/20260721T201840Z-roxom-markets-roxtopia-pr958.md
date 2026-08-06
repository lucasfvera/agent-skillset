---
id: 20260721T201840Z-roxom-markets-roxtopia-pr958
status: actioned
capturedAt: 2026-07-21T20:18:40Z
actionedAt: 2026-08-06T18:40:26Z
pr: roxom-markets/roxtopia#958
prUrl: https://github.com/roxom-markets/roxtopia/pull/958
fixCommitSha: d752c6913d45d58d9d69e1ed64b50455a015d314
threadCount: 2
---

# Session capture — roxom-markets/roxtopia#958

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6StiDq |
| **path** | packages/shared/src/header/notification-center/helpers.ts |
| **line** | 67 |
| **verdict** | partially_valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/notification-center/helpers.ts, packages/shared/src/header/notification-center/helpers.test.ts, packages/shared/src/header/notification-center/normalizeNotificationMessages.ts, packages/shared/src/header/notification-center/index.ts, packages/shared/src/index.ts |

### Reviewer comment

This doesn't make much sense, the instrumentId will always look like an instrumentId...
The return empty could be avoided by just returning what we have and handling it in any other end, like with a loading or empty string until it actually loads.

Is there any reason why you think the instrumentId won't be the uuid?

### Resolution

Partially valid. You are right that when `currency` is an instrument id it is always UUID-shaped, and that the intermittent bug is a catalog loading race.

`resolveInstrumentTicker` now returns the unresolved value again. Call sites suppress UUID-shaped tickers (generic copy) until the catalog resolves — including deposit/withdrawal, contract symbols, and loan principal fallback. The UUID vs symbol check still matters because some publishers put a ticker symbol in `currency` (eventrox) while others put the instrument id (tx).

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | review:4748640322 |
| **path** | — |
| **line** | — |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/notification-center/helpers.ts, packages/shared/src/header/notification-center/normalizeNotificationMessages.ts, packages/shared/src/header/notification-center/helpers.test.ts, packages/shared/src/index.ts |

### Reviewer comment

I think the issue is related to loading times right? It seems that until we find the instrument, it resolves as undefined and we show the instrumentId.

### Resolution

Valid. The intermittent title bug is a loading-race: until the instruments catalog resolves the id, we used to render the raw instrument UUID. Call sites now suppress UUID-shaped tickers until the catalog is ready.
