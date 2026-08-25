---
id: 20260821T005847Z-roxom-markets-roxtarsverse-pr824
status: actioned
capturedAt: 2026-08-21T00:58:47Z
actionedAt: 2026-08-25T02:59:47Z
pr: roxom-markets/roxtarsverse#824
prUrl: https://github.com/roxom-markets/roxtarsverse/pull/824
fixCommitSha: fc2f627777d8a5ae5e650869080bd22fa4e865f3
threadCount: 2
---

# Session capture — roxom-markets/roxtarsverse#824

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOObcV4c6bAMpz |
| **path** | apps/roxtars/tests/integration/grpc/users/setAntiPhishingCode.integration.test.ts |
| **line** | 1 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | apps/roxtars/tests/integration/grpc/users/setAntiPhishingCode.integration.test.ts |

### Reviewer comment

Wait, you are testing the handler. You are not doing the actual integration test where we create the client and call the method through the proper client as we do in the actual integration tests. We should be testing the actual grpc call to the proper method.

### Resolution

Valid. The suite now creates `UsersServiceClient` and calls `setAntiPhishingCode` against the live gRPC server that `testFactory` already starts.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOObcV4c6bAOb8 |
| **path** | apps/roxtars/src/infrastructure/repository/antiPhishingCodesRepository.ts |
| **line** | 9 |
| **verdict** | dismissed |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Can't we get this constant from a library we already have installed? Are we doing something similar in other places? It seems weird to have the hardcoded value of an error from psql. We can keep it like this if this is the only place where we have it.

### Resolution

Keeping as-is. `pg` does not export named SQLSTATE constants, and `23503` is only used here. Unique violations use `PG_UNIQUE_CONSTRAINT_ERROR_CODE` (`23505`) or a hardcoded `23505` elsewhere — a different code.
