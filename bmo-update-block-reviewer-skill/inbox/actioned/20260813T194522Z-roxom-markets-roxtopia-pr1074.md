---
id: 20260813T194522Z-roxom-markets-roxtopia-pr1074
status: actioned
capturedAt: 2026-08-13T19:45:22Z
actionedAt: 2026-08-25T02:59:47Z
pr: roxom-markets/roxtopia#1074
prUrl: https://github.com/roxom-markets/roxtopia/pull/1074
fixCommitSha: 0166a75a898de63632544ab6039673148c3f2fb2
threadCount: 3
---

# Session capture — roxom-markets/roxtopia#1074

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6ZD2_t |
| **path** | packages/shared/src/one-click-trade/__tests__/BuySellForm/BuySellForm.test.tsx |
| **line** | 951 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/one-click-trade/__tests__/BuySellForm/BuySellForm.test.tsx |

### Reviewer comment

We should use `userEvent` instead. `fireEvent` is legacy.

### Resolution

Valid. Switched this case to `userEvent.setup()` and `user.type` on the buy field.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6ZD3oC |
| **path** | packages/shared/src/one-click-trade/__tests__/BuySellForm/BuySellForm.test.tsx |
| **line** | 949 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/one-click-trade/__tests__/BuySellForm/BuySellForm.test.tsx |

### Reviewer comment

Do we need the type assertions? Don't we get the typing out of the box with the locator?

### Resolution

Valid. Dropped `as HTMLInputElement` and asserted with `toHaveValue` from the locator.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6ZD9DQ |
| **path** | packages/shared/src/one-click-trade/client/TradeForm.tsx |
| **line** | 1877 |
| **verdict** | partially_valid |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Instead of a `useEffect`, would it be better to add the validation to the handler instead? Like triggering on the `onChange` event the validation. How are we triggering the validation the other way around? Are we using an effect too?

### Resolution

Partially valid. Sell-first already validates from `onChange` (`scheduleFromValidation`); buy `onChange` already calls `scheduleToValidation`. The effect stays so we re-validate when the derived sell amount appears after a quote, which does not fire `onChange`.
