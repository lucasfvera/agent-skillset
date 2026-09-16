---
id: 20260903T183130Z-roxom-markets-roxtopia-pr1178
status: actioned
capturedAt: 2026-09-03T18:31:30Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1178
prUrl: https://github.com/roxom-markets/roxtopia/pull/1178
fixCommitSha: 0d7221f011c808a26a2c6d27bcb3e36af7830971
threadCount: 3
---

# Session capture — roxom-markets/roxtopia#1178

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6fBEEO |
| **path** | packages/shared/src/header/dropdown-assets-menu/__tests__/DropdownAssetsMenu.test.tsx |
| **line** | 193 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/dropdown-assets-menu/__tests__/DropdownAssetsMenu.test.tsx |

### Reviewer comment

We will implement the ability to show BTC estimates under the same toggle so the description should avoid referring to USD directly since we are referring to the estimates as a whole and the suites are not tied to USD.

### Resolution

Valid. Renamed the suite and cases to talk about estimates, not USD, so they stay accurate when BTC estimates share the same toggle.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6fBRN0 |
| **path** | packages/shared/src/header/dropdown-assets-menu/index.tsx |
| **line** | 61 |
| **verdict** | dismissed |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Don't we have this component or something similar that we can reuse from the accounts page left panel? I know we have a similar behavior in place but maybe it doesn't apply to this component.

### Resolution

Keeping as-is. The accounts sidebar and `AccountNavSummary` already compose `UsdValue` + `HideWrapper` inline — there is no extracted estimate widget to import. `BalanceItem` uses a different formatter in exchange, so it does not apply here.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOQ59d5s6fB8Zg |
| **path** | packages/shared/src/header/dropdown-assets-menu/index.tsx |
| **line** | 203 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | packages/shared/src/header/dropdown-assets-menu/index.tsx |

### Reviewer comment

I think is overkill to add a loading state here as well. If it is tied to the same loading, we can just avoid showing the estimate until it is loaded. So we end up with a single skeleton and avoid this extra skeleton

### Resolution

Valid. Removed the extra skeleton. The estimate stays hidden until the existing total-balance load finishes, so only one skeleton remains.
