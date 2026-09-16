---
id: 20260907T172615Z-roxom-markets-roxtopia-pr1197
status: actioned
capturedAt: 2026-09-07T17:26:15Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1197
prUrl: https://github.com/roxom-markets/roxtopia/pull/1197
fixCommitSha: d0298be4cbb595cd2771bfb8541512a2b0b019e1
threadCount: 1
---

# Session capture — roxom-markets/roxtopia#1197

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | review:5134284093 |
| **path** | — |
| **line** | — |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/components/CurrencyValue/Symbol.tsx, packages/shared/src/ticker-marquee/TickerPriceDisplay.tsx, packages/shared/src/components/CurrencyValue/__tests__/Symbol.test.tsx |

### Reviewer comment

The price symbol shows up without the proper alignment for USD

<img width="180" height="74" alt="Image" src="https://github.com/user-attachments/assets/f3b5a07f-96ef-4f8e-9388-197eda428feb" />

### Resolution

Valid. The USD `$` was boxed with icon `size-*` classes meant for SVG glyphs, so it sat off the digits. `$` now inherits the parent type and the marquee price row is baseline-aligned.
