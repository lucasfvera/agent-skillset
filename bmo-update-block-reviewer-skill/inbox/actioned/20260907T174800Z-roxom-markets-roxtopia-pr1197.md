---
id: 20260907T174800Z-roxom-markets-roxtopia-pr1197
status: actioned
capturedAt: 2026-09-07T17:48:00Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1197
prUrl: https://github.com/roxom-markets/roxtopia/pull/1197
fixCommitSha: 5d46b248294320d6c2aabc1750004cac139b0fbe
threadCount: 2
---

# Session capture — roxom-markets/roxtopia#1197

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6f_fcg |
| **path** | packages/shared/src/components/CurrencyValue/__tests__/Symbol.test.tsx |
| **line** | 18 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/components/CurrencyValue/__tests__/Symbol.test.tsx |

### Reviewer comment

We should not test classes. It is brittle and these tests are not design for that. Remove the test if you do not find a proper way to test this behavior following our best practices in our tests.

### Resolution

Valid. Removed the class-asserting Symbol test. Alignment is visual CSS and those assertions are too brittle for this suite; TickerPriceDisplay still covers USD digits and percent.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6f_oqm |
| **path** | packages/shared/src/ticker-marquee/TickerPriceDisplay.tsx |
| **line** | 80 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/ticker-marquee/TickerPriceDisplay.tsx |

### Reviewer comment

Why are we using baseline instead of center? I think there is an alignment issue due to setting this to baseline.

### Resolution

Valid. Restored `items-center` on the price row. The USD alignment fix stays in Symbol: `$` no longer gets icon size boxes.
