---
id: 20260903T193650Z-roxom-markets-roxtopia-pr1182
status: actioned
capturedAt: 2026-09-03T19:36:50Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1182
prUrl: https://github.com/roxom-markets/roxtopia/pull/1182
fixCommitSha: e67bd3a92
threadCount: 1
---

## Thread 1

- threadId: PRRT_kwDOQ59d5s6fDM7j
- path: packages/shared/src/components/price-type-toggle/__tests__/CombinedPriceTypeToggle.test.tsx
- line: 145
- verdict: valid
- reviewer: lucasfvera
- changedFiles:
  - packages/shared/src/components/price-type-toggle/__tests__/CombinedPriceTypeToggle.test.tsx

### Reviewer comment

No need to test this. Remove it. Testing styles is brittle and doesn't add value in this type of tests.

### Resolution

Valid. Removed the style-class test and kept the existing behavior coverage for the price-type toggle.

Block review found no issues with the test removal before push.
