---
id: 20260907T155600Z-roxom-markets-roxtopia-pr1194
status: actioned
capturedAt: 2026-09-07T15:56:00Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1194
prUrl: https://github.com/roxom-markets/roxtopia/pull/1194
fixCommitSha: 179615e673eec4072a18cdaad34a423c11597f47
threadCount: 3
---

# Session capture — roxom-markets/roxtopia#1194

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6f9_pE |
| **path** | packages/shared/src/components/CurrencyValue/index.tsx |
| **line** | 1 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/components/CurrencyValue/index.tsx |

### Reviewer comment

Why do we need to pass down value and satsValue? I'm confused.

### Resolution

Valid. `value` is the painted digits (signed, compacted, or already converted USD). `satsValue` is the original amount for the BTC estimate — deriving sats from a USD string would treat dollars as bitcoin. Documented that dual contract on CurrencyValue.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6f-D36 |
| **path** | apps/exchange/src/components/Accounts/Funding/FundingPortfolio/FundingPortfolioShared.tsx |
| **line** | 229 |
| **verdict** | partially_valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/components/CurrencyValue/index.tsx |

### Reviewer comment

Is it accurate to still call this `usdValueOptions`?

### Resolution

Partially valid. The name is leftover from when the subtitle was always USD; renaming the public prop would touch 40+ call sites including terminal vendor copies. Documented that `usdValueOptions.show` now gates the counter-estimate (BTC under converted USD, otherwise USD). Block review asked to align `@example` captions with counter-estimate wording; those captions were updated before publish.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6f-GwE |
| **path** | apps/exchange/src/test/components/Account/Help/TotalEquityHelpModal.test.tsx |
| **line** | 80 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | apps/exchange/src/test/components/Account/Help/TotalEquityHelpModal.test.tsx |

### Reviewer comment

Why do we need this type assertion? Can we easily avoid it?

### Resolution

Valid. The mock is typed as PriceType, so the formatter call no longer needs an assertion. Assignments use PriceType.BTC / PriceType.USD. The hoisted initializer still annotates PriceType because vi.hoisted runs before imports.
