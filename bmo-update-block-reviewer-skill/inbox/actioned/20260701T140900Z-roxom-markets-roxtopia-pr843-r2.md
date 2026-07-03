---
id: 20260701T140900Z-roxom-markets-roxtopia-pr843-r2
status: actioned
capturedAt: 2026-07-01T14:09:00Z
actionedAt: 2026-07-01T19:18:27Z
pr: roxom-markets/roxtopia#843
prUrl: https://github.com/roxom-markets/roxtopia/pull/843
fixCommitSha: 43781fe4a4216d0951dda903f175b974dd73bf53
threadCount: 3
---

## Thread 1

- threadId: PRRT_kwDOQ59d5s6NmbTq
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 122
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
What is this for? For regex, always include a small comment to make sure we understand what it does.

**Resolution:**
Valid. Extracted `INTEGER_SCALED_STRING_PATTERN` with a comment: optional minus, digits only — matches Hermod `ScaledInteger` string shape.

## Thread 2

- threadId: PRRT_kwDOQ59d5s6NmecD
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 161
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
Still not sure what are you trimming here. Why do you assume that the string will have whitespaces?

**Resolution:**
Valid. Removed `trim()`. We do not expect padded strings on this path; the regex rejects whitespace, so trimming was unnecessary.

## Thread 3

- threadId: PRRT_kwDOQ59d5s6Nmomm
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 179
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
If we use Number on a number type, it still works. Why do we need the extra type check?

**Resolution:**
Valid. Simplified to `Number(rawAmount)` since it is a no-op on numbers and coerces bigint/string in the display-float branch.
