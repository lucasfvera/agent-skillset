---
id: 20260703T162759Z-roxom-markets-roxtarsverse-pr751
status: actioned
capturedAt: 2026-07-03T16:27:59Z
actionedAt: 2026-08-06T18:40:26Z
pr: roxom-markets/roxtarsverse#751
prUrl: https://github.com/roxom-markets/roxtarsverse/pull/751
fixCommitSha: d58341e22e6b8f88e71c0acc3a1b7e61011c1a4a
threadCount: 4
---

## Thread 1

- threadId: PRRT_kwDOObcV4c6OOp8J
- path: apps/tx/tests/integration/helpers/withdrawalNotificationContext.ts
- line: 2
- verdict: valid
- reviewer: lucasfvera
- changedFiles:
  - apps/tx/tests/integration/helpers/withdrawalNotificationContext.ts

### Reviewer comment

You forgot to run linters? Why is this unused variable here?

### Resolution

Valid. Removed the unused import from the helper and reran lint on the touched files so the harness stays clean.

## Thread 2

- threadId: PRRT_kwDOObcV4c6OOrLX
- path: apps/tx/tests/integration/flows/withdrawalNotifications.integration.test.ts
- line: 32
- verdict: valid
- reviewer: lucasfvera
- changedFiles:
  - apps/tx/tests/integration/flows/withdrawalNotifications.integration.test.ts

### Reviewer comment

Why are you mocking the yuta component instead of using the mock that's used in other tests? Is there a valid reason that we need to mock it here like this?

### Resolution

Valid. Switched this spec to reuse the shared Yuta component mock directly, so it no longer carries a one-off mock shape.

## Thread 3

- threadId: PRRT_kwDOObcV4c6OO4IT
- path: apps/tx/tests/integration/helpers/withdrawalNotificationContext.ts
- line: 43
- verdict: valid
- reviewer: lucasfvera
- changedFiles:
  - apps/tx/tests/integration/helpers/withdrawalNotificationContext.ts
  - apps/tx/src/api/handlers/withdrawals/createWithdrawal.handler.ts

### Reviewer comment

I see we define several types in the helpers. Why do we need to define (or redefine) these types? Can't we use the actual source of truth for these types? This will avoid divergence from the actual implementation making the tests more robust.

### Resolution

Valid. Replaced the helper-local contract types with source-of-truth service and publish signatures from the app code so the test stays aligned with implementation changes.

## Thread 4

- threadId: PRRT_kwDOObcV4c6OO8w3
- path: apps/tx/tests/integration/helpers/withdrawalNotificationContext.ts
- line: 182
- verdict: valid
- reviewer: lucasfvera
- changedFiles:
  - apps/tx/tests/integration/helpers/withdrawalNotificationContext.ts
  - apps/tx/src/api/handlers/withdrawals/createWithdrawal.handler.ts

### Reviewer comment

Is the `never` typing and the `unknown` type really needed? Is this something we do in other tests as well?

### Resolution

Valid. Removed the `never` and `unknown` shortcuts by using explicit typed no-op stubs in the harness and narrowing the handler dependency container to the subset it actually reads.
