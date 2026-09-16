---
id: 20260902T200615Z-roxom-markets-roxtopia-pr1175
status: actioned
capturedAt: 2026-09-02T20:06:15Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1175
prUrl: https://github.com/roxom-markets/roxtopia/pull/1175
fixCommitSha: c08d91f92becfbc30302181ae77b2ebb116d1f2a
threadCount: 2
---

# Session capture — roxom-markets/roxtopia#1175

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6eqRVZ |
| **path** | apps/exchange/src/components/OrderTicket/index.test.tsx |
| **line** | 54 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | apps/exchange/src/components/OrderTicket/index.test.tsx |

### Reviewer comment

I don't want negative use cases tests. We should test what we want and not what we removed or it is no longer required. These negative tests only apply if we are fixing a bug or a regression.

### Resolution

Valid. Removed the funding-card absence asserts and that mock. The spec now only checks that the futures and spot tickets render.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6eqUL7 |
| **path** | apps/exchange/src/components/TradingCards/FuturesOrderPanelCard/index.test.tsx |
| **line** | 72 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | apps/exchange/src/components/TradingCards/FuturesOrderPanelCard/index.test.tsx |

### Reviewer comment

It is wrong to tie the test description to the flag since we are intentionally untangling one from the other. It doesn't make sense to write it like this because turning the flag on won't change anything. We need to describe it as the positive case without the conditional from the flag.

### Resolution

Valid. Holdings is now a positive case — the title no longer mentions the flag. Product-filter tests stay flag-aware because that gate is still real.
