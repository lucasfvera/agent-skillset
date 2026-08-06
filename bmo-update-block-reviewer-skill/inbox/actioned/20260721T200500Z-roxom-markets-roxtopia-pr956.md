---
id: 20260721T200500Z-roxom-markets-roxtopia-pr956
status: actioned
capturedAt: 2026-07-21T20:05:00Z
actionedAt: 2026-08-06T18:40:26Z
pr: roxom-markets/roxtopia#956
prUrl: https://github.com/roxom-markets/roxtopia/pull/956
fixCommitSha: fbde5a2ad5ace9981818f9c60d17f92f4d12df87
threadCount: 1
---

# Session capture — roxom-markets/roxtopia#956

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | review:4748560616 |
| **path** | — |
| **line** | — |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | apps/exchange/src/components/TradingCards/FuturesOrderPanelCard/TabContentPositions.tsx |

### Reviewer comment

The proposed solution is not working in my local. Check how we solve it in other tables, I think we add some extra padding to the bottom. Check the holdings tab for instance.
If there is no clear solution to replicated you can propose any other that actually work.

### Resolution

Valid. Dropping `overflow-y-clip` alone was not enough on short Futures viewports. Open Positions now mirrors Holdings: `overflow-x-auto px-1 pb-1` plus `TRADING_ACCOUNT_ASSETS_TABLE_MIN_HEIGHT_CLASS` so the last row can scroll clear of the fixed ticker footer.
