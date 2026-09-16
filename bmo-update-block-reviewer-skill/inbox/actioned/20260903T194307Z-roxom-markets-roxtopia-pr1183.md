---
id: 20260903T194307Z-roxom-markets-roxtopia-pr1183
status: actioned
capturedAt: 2026-09-03T19:43:07Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1183
prUrl: https://github.com/roxom-markets/roxtopia/pull/1183
fixCommitSha: 1eeede58d963a7d903fcaef775746a657a888541
threadCount: 1
---

# Session capture — roxom-markets/roxtopia#1183

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6fDakK |
| **path** | packages/shared/src/preferences/complementaryEstimateUnit.ts |
| **line** | 28 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/preferences/complementaryEstimateUnit.ts, packages/shared/src/preferences/__tests__/complementaryEstimateUnit.test.ts, packages/shared/src/preferences/__tests__/PreferencesContent.test.tsx |

### Reviewer comment

The preview for BTC should also be a dynamic value as we have for the USD preview. We should show the equivalent BTC value of 1 USD with the BTC precision (8 decimals)

### Resolution

Valid. The BTC sample now shows 1 USD in BTC at 8-decimal precision (`BTC.PRECISION.BTC`), and falls back to "visible" when the price is missing—same as the USD sample.
