---
id: 20260914T142149Z-roxom-markets-roxtarsverse-pr823
status: actioned
capturedAt: 2026-09-14T14:21:49Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtarsverse#823
prUrl: https://github.com/roxom-markets/roxtarsverse/pull/823
fixCommitSha: 8a042d316254e33b415112340f9f94b5b91c2417
threadCount: 1
---

# Session capture — roxom-markets/roxtarsverse#823

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | review:5183301445 |
| **path** | — |
| **line** | — |
| **verdict** | partially_valid |
| **reviewer** | dieduro |
| **changedFiles** | apps/roxtars/src/api/grpcHandlers/users/getAntiPhishingCodeMask.handler.ts, apps/roxtars/protorox.config.js, apps/roxtars/src/generated/users.ts, apps/roxtars/src/proto/users.proto, apps/roxtars/tests/constants/configs.ts, apps/roxtars/tests/integration/grpc/users/getAntiPhishingCodeMask.integration.test.ts, apps/roxtars/tests/unit/api/grpc/getAntiPhishingCodeMask.test.ts |

### Reviewer comment

Review: PRs #823, #824, #825 — Anti-Phishing Code RPCs
Do not merge these PRs as a stack.
Structure
1. The three PRs change the same files. Each PR uses a different shape for the service, the repository, and the types.
2. ~#824 and #825 add the same migration file. This migration is already on main through PR #822.~
3. Close #823, #824, and #825. Make one PR with three RPCs. Rebase it on main.
4. Use one service and one repository in the new PR. Do not re-generate the same files again.
Security
5. The handlers do not check the format of user_id. A bad UUID will give an error from the database. Add a UUID check before you call the service. Return INVALID_USER_ID when the check fails.
6. The handlers send raw database errors to the caller. Send a generic message instead. Put the full error in the logs only.
7. The table does not check the code format. The service has a rule for the format. Add a CHECK constraint to the table. Keep the rule and the constraint equal.
8. The code is a secret. GetAntiPhishingCode returns it to every caller on the network. Accept this risk for now. Make a ticket for a caller-identity check across all services. (Team decision: services trust each other today.)
Performance
 9. #825 opens a transaction for one SELECT. Do not use a transaction for a read. Use the pattern from #823.
10. #824 opens the transaction before the code validation. Validate first. Then open the transaction. This step keeps free connections for bad requests.
Legibility / hygiene
11. mapSetAntiPhishingCodeError compares error strings. One typo will give a wrong error code. Use the same constants on both sides, or use typed errors.
12. #824 uses catch (error: any). Use catch (error: unknown). Then use instanceof Error to get the message. The other PRs do this correctly.
13. #823 changes the protoc version in the generated code. #825 adds a hand-written generated file. Fix protorox.config.js in the new PR. Then all future generation is reproducible.
14. #823 puts its test file in grpc/. The other PRs use grpc/users/. Use one location.
15. Each test file has a different hard-coded port. Use one shared constant or a config value.
16. users.proto has no new line at the end of the file. Add it.
17. #825 logs hasCode: true before it returns the code. This is safe. Keep the log test. Do not log the code itself.
Good work
18. The table design is good. One row per user, unique index, delete cascade.
19. The upsert is clean. The tests confirm the replace behavior.
20. The tests check for leaks of the code in responses, in logs, and in user fetches. Keep these tests in the new PR.

### Resolution

Partially valid. Shipped the #823 items: UUID check on `user_id`, generic gRPC errors, pinned `protorox.config.js` / regenerated `users.ts` with grpc-tools 3.19.1, moved the spec under `grpc/users/`, shared test port, and a trailing newline on `users.proto`. Combining #823/#824/#825 (items 1/3/4) stays with the coordinator. Items 7–12, 17, and 19 belong to #824 / #825 and were not changed here.

Block review dropped an overlapping malformed-UUID integration case (`no-overlapping-method-tests`) and an indirect `JSON.stringify` leak assertion (`no-unproven-indirect-assertions`).
