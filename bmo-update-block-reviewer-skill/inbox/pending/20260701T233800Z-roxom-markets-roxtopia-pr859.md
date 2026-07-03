---
id: 20260701T233800Z-roxom-markets-roxtopia-pr859
status: pending
capturedAt: 2026-07-01T23:38:00Z
actionedAt: null
pr: roxom-markets/roxtopia#859
prUrl: https://github.com/roxom-markets/roxtopia/pull/859
fixCommitSha: 88cc6c2eb80d342d546ef849a767fe37367b6157
threadCount: 5
---

# Session capture — roxom-markets/roxtopia#859

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6NveYO |
| **path** | packages/shared/src/header/notification-center/helpers.ts |
| **line** | 70 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/notification-center/helpers.ts |

### Reviewer comment

We should never use loose inequality...

### Resolution

Valid. Replaced loose `!= null` with strict `!== undefined` and `!== null` inside the extracted `isBtcFundingNotification` helper.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6Nveq- |
| **path** | packages/shared/src/header/notification-center/helpers.ts |
| **line** | 68 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/notification-center/helpers.ts |

### Reviewer comment

Why do we need so many checks to know if it is BTC?

### Resolution

Valid. Collapsed the inline OR into `isBtcFundingNotification(ticker, instrument)`, preserving `ticker === "BTC" || isBtcInstrument(instrument)` semantics with strict null checks.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6NvhiI |
| **path** | packages/shared/src/header/notification-center/helpers.ts |
| **line** | 63 |
| **verdict** | dismissed |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Some logic seems duplicated with the one click trade method, formatOneClickOrderBaseAmount. If that's so, would it be valuable to refactor both and make sure we reuse the logic? No need to force it though.

### Resolution

Keeping as-is. The dual-path pattern is aligned, but funding notifications use `resolveFundingNotificationDecimals`, a BTC-specific branch, and always return a string — one-click uses capped `baseDecimals`, null for empty wire values, and `formatTrimmedBaseUnits`. A shared helper would add indirection without much gain for this PR scope.

## Thread 4

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6Nvh3U |
| **path** | packages/shared/src/header/notification-center/helpers.ts |
| **line** | 107 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/notification-center/helpers.ts |

### Reviewer comment

Remember that we shouldn't use magic numbers.

### Resolution

Valid. Replaced the literal `20` with `DEFAULT_MAX_DISPLAY_FRACTION_DIGITS` next to the other display defaults.

## Thread 5

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6NviqM |
| **path** | packages/shared/src/header/notification-center/helpers.test.ts |
| **line** | 1 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/notification-center/helpers.test.ts |

### Reviewer comment

For tests we should have the AAA pattern, extracting queries and variables into their own block to ensure that the tests are readable and easier to understand

### Resolution

Valid. Refactored `formatNotificationAmount` tests to Arrange (`amount`, `ticker`, `instrument`) / Act (`formatted`) / Assert (`expect`), with hoisted `btcInstrument` and `BTC_*` named constants.
