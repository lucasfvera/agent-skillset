---
id: 20260914T143423Z-roxom-markets-roxtarsverse-pr824
status: actioned
capturedAt: 2026-09-14T14:34:23Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtarsverse#824
prUrl: https://github.com/roxom-markets/roxtarsverse/pull/824
fixCommitSha: a2b6be4912f0e8070a6186db37c0dd3e350c5215
threadCount: 11
---

# Session capture — roxom-markets/roxtarsverse#824

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

Review 5183301445 was posted on #823 with no inline threads. Replies for 824-assigned items went on #824 as a top-level follow-up.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-5 |
| **path** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts |
| **line** | 53 |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts, apps/roxtars/tests/integration/grpc/users/setAntiPhishingCode.integration.test.ts |

### Reviewer comment

5. The handlers do not check the format of user_id. A bad UUID will give an error from the database. Add a UUID check before you call the service. Return INVALID_USER_ID when the check fails.

### Resolution

Valid. Handler returns `INVALID_USER_ID` for empty or non-RFC-4122 ids before the service.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-6 |
| **path** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts |
| **line** | 75 |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts, apps/roxtars/src/core/service/AntiPhishingCodesService.ts, apps/roxtars/src/infrastructure/repository/antiPhishingCodesRepository.ts |

### Reviewer comment

6. The handlers send raw database errors to the caller. Send a generic message instead. Put the full error in the logs only.

### Resolution

Valid. Domain messages stay; unmapped failures return `Internal server error` and log the full error.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-7 |
| **path** | apps/roxtars/src/core/service/AntiPhishingCodesService.ts |
| **line** | 7 |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | migrations/1789394687190_anti-phishing-codes-code-format-check.sql, apps/roxtars/src/core/service/AntiPhishingCodesService.ts, apps/roxtars/tests/integration/migrations/antiPhishingCodes.integration.test.ts |

### Reviewer comment

7. The table does not check the code format. The service has a rule for the format. Add a CHECK constraint to the table. Keep the rule and the constraint equal.

### Resolution

Valid. New migration `anti_phishing_codes_code_format_check` matches `ANTI_PHISHING_CODE_PATTERN_SOURCE`. Block review: assert the CHECK via Postgres `23514`, hardcoded at the test site with the errcodes appendix comment.

## Thread 4

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-10 |
| **path** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts |
| **line** | 67 |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts, apps/roxtars/src/core/service/AntiPhishingCodesService.ts |

### Reviewer comment

10. #824 opens the transaction before the code validation. Validate first. Then open the transaction. This step keeps free connections for bad requests.

### Resolution

Valid. `normalizeAntiPhishingCode` runs before `startTransaction`.

## Thread 5

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-11 |
| **path** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts |
| **line** | 12 |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts, apps/roxtars/src/core/service/AntiPhishingCodesService.ts, apps/roxtars/src/infrastructure/repository/antiPhishingCodesRepository.ts |

### Reviewer comment

11. mapSetAntiPhishingCodeError compares error strings. One typo will give a wrong error code. Use the same constants on both sides, or use typed errors.

### Resolution

Valid. Mapper and repository share `ANTI_PHISHING_CODE_ERROR`; the map is a `Record` keyed by those constants.

## Thread 6

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-12 |
| **path** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts |
| **line** | 101 |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/src/api/grpcHandlers/users/setAntiPhishingCode.handler.ts, apps/roxtars/src/core/service/AntiPhishingCodesService.ts, apps/roxtars/src/infrastructure/repository/antiPhishingCodesRepository.ts |

### Reviewer comment

12. #824 uses catch (error: any). Use catch (error: unknown). Then use instanceof Error to get the message. The other PRs do this correctly.

### Resolution

Valid. Handler, service, and repository use `unknown` and `instanceof Error`.

## Thread 7

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-13 |
| **path** | — |
| **line** | — |
| **verdict** | dismissed |
| **reviewer** | dieduro |
| **changedFiles** | — |

### Reviewer comment

13. #823 changes the protoc version in the generated code. #825 adds a hand-written generated file. Fix protorox.config.js in the new PR. Then all future generation is reproducible.

### Resolution

Keeping as-is. Config fix is on 823/825; this branch does not hand-edit generated `users.ts`.

## Thread 8

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-15 |
| **path** | apps/roxtars/tests/integration/grpc/users/setAntiPhishingCode.integration.test.ts |
| **line** | 17 |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/tests/constants/configs.ts, apps/roxtars/tests/integration/grpc/users/setAntiPhishingCode.integration.test.ts |

### Reviewer comment

15. Each test file has a different hard-coded port. Use one shared constant or a config value.

### Resolution

Valid. Port 50269 lives on `TEST_CONFIGS.INTEGRATION.GRPC.users.setAntiPhishingCode`. Block review: do not add a grpc-folder ports file; match the tx `TEST_CONFIGS` shape. This PR only registers the Set suite key.

## Thread 9

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-16 |
| **path** | apps/roxtars/src/proto/users.proto |
| **line** | — |
| **verdict** | valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/src/proto/users.proto |

### Reviewer comment

16. users.proto has no new line at the end of the file. Add it.

### Resolution

Valid. File now ends with a newline.

## Thread 10

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-19 |
| **path** | apps/roxtars/tests/integration/grpc/users/setAntiPhishingCode.integration.test.ts |
| **line** | — |
| **verdict** | dismissed |
| **reviewer** | dieduro |
| **changedFiles** | — |

### Reviewer comment

19. The upsert is clean. The tests confirm the replace behavior.

### Resolution

Keeping as-is. Replace-in-place coverage stays.

## Thread 11

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445-item-20 |
| **path** | apps/roxtars/tests/integration/migrations/antiPhishingCodes.integration.test.ts |
| **line** | — |
| **verdict** | dismissed |
| **reviewer** | dieduro |
| **changedFiles** | — |

### Reviewer comment

20. The tests check for leaks of the code in responses, in logs, and in user fetches. Keep these tests in the new PR.

### Resolution

Keeping as-is. Generic user-fetch leak coverage stays.
