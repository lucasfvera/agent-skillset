---
id: 20260914T214941Z-roxom-markets-roxtopia-pr1231
status: actioned
capturedAt: 2026-09-14T21:49:41Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1231
prUrl: https://github.com/roxom-markets/roxtopia/pull/1231
fixCommitSha: 676e13badf9eb129a490fa3a9a4c66fc211f3495
threadCount: 1
---

# Session capture — roxom-markets/roxtopia#1231

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6iSCxT |
| **path** | apps/terminal/src/lib/market-data/denom.ts |
| **line** | 17 |
| **verdict** | valid |
| **reviewer** | nicolasmartello-coder |
| **changedFiles** | apps/terminal/src/lib/market-data/denom.ts, apps/terminal/src/lib/market-data/denom.test.ts, apps/terminal/tsconfig.json, apps/terminal/vitest.config.mts |

### Reviewer comment

We should read this https://github.com/roxom-markets/roxtopia/blob/f8f0cc8524a8aedf14cd6e3ae5a23748c045e6cd/packages/shared/src/types/priceType.ts#L9 instead of using this custom array. In that way we can avoid this kind of visual issue again if we add, remove or sort the price items.

### Resolution

Valid. Markets chips now alias `PRICE_TYPES` from `packages/shared/src/types/priceType.ts`, so adding, removing, or sorting units updates both toggles.
