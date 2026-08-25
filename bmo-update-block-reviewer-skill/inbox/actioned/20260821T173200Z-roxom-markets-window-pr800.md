---
id: 20260821T173200Z-roxom-markets-window-pr800
status: actioned
capturedAt: 2026-08-21T17:32:00Z
actionedAt: 2026-08-25T02:59:47Z
pr: roxom-markets/window#800
prUrl: https://github.com/roxom-markets/window/pull/800
fixCommitSha: 011ba0343a9a4d40952e21d6baf6f56bc78d037d
threadCount: 4
---

# Session capture — roxom-markets/window#800

Captured by [`bmo-respond-pr-review`](../../bmo-respond-pr-review/SKILL.md). Raw thread context for later abstraction. Do not edit after capture.

## Thread 1

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6bO_D6 |
| **path** | src/routes/handlers/account/anti-phishing-code/getAntiPhishingCodeMask.handler.ts |
| **line** | 57 |
| **verdict** | valid |
| **reviewer** | lucasfvera |
| **changedFiles** | src/routes/handlers/account/anti-phishing-code/getAntiPhishingCodeMask.handler.ts, tests/unit/getAntiPhishingCodeMask.handler.test.ts |

### Reviewer comment

Why are we re-defining the values from the result? If we want type safety we can include zod to check the typing that we get. But the contract already says that if the response is successful that's the expected payload. If we want to double check lets do it with Zod. Follow existing patterns in the codebase that declare zod schemas if you use that.

### Resolution

Valid. The handler now parses `result.data` with `AntiPhishingCodeMaskBodySchema` and returns `{ hasCode, mask: mask ?? null }`, so extra keys are stripped and omitted `mask` becomes JSON `null`. Parse failure is a generic 400 without echoing the payload.

Block-review findings applied: restore projected `{ hasCode, mask }` body assertion; add Zod parse-failure 400 leak test.

## Thread 2

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6bPB-X |
| **path** | tests/unit/getAntiPhishingCodeMask.handler.test.ts |
| **line** | 87 |
| **verdict** | dismissed |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

If the endpoint expects authenticated users, does this endpoint gets called without a session? Or is the session not related to the authentication in this case?

### Resolution

Keeping as-is. The route only uses `rateLimitMiddleware`; the session is the auth, and `handleRequest` can yield a request with no user. Unauthenticated callers can hit this path, so the 401 when the flag is on and `user.id` is missing matches sibling account handlers.

## Thread 3

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6bPEvU |
| **path** | tests/unit/getAntiPhishingCodeMask.handler.test.ts |
| **line** | 116 |
| **verdict** | partially_valid |
| **reviewer** | lucasfvera |
| **changedFiles** | tests/unit/getAntiPhishingCodeMask.handler.test.ts |

### Reviewer comment

Does it makes sense to check the values received from roxtars? We are mocking the response so I don't think it adds real value to test it right? We need to cover what is inherent to window service, if we are mocking roxtars we only want to test that the proper methods are called.

### Resolution

Partially valid. Dropped the fake `antiPhishingCode` / `code` keys. Kept Window-owned coverage: the gRPC method is called with `{ userId }`, Zod projects only `{ hasCode, mask }`, omitted proto `mask` becomes JSON `null`, and the body/logs still cannot leak a full code.

Block-review findings applied: restore `expect(body).toEqual({ hasCode: true, mask: MASK })` as Window's HTTP contract; drop redundant `not.toHaveProperty('extraField')`.

## Thread 4

| Field | Value |
|-------|-------|
| **threadId** | PRRT_kwDOMvQwAc6bPHqb |
| **path** | src/routes/handlers/account/anti-phishing-code/getAntiPhishingCodeMask.handler.ts |
| **line** | 1 |
| **verdict** | dismissed |
| **reviewer** | lucasfvera |
| **changedFiles** | — |

### Reviewer comment

Are we passing down a request id for tracing it in other services? I believe that this is a stablished patter in the codebase. If not, why not?

### Resolution

Keeping as-is. `request_id` is the RabbitMQ RPC metadata pattern. The generated Users Service client only passes a deadline, same as `deleteAccount` and `patchPreferences`, so this handler cannot attach tracing metadata without changing generated gRPC plumbing.
