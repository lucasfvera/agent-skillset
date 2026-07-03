---
id: 20260701T132500Z-roxom-markets-roxtopia-pr843
status: actioned
capturedAt: 2026-07-01T13:25:00Z
actionedAt: 2026-07-01T19:18:27Z
pr: roxom-markets/roxtopia#843
prUrl: https://github.com/roxom-markets/roxtopia/pull/843
fixCommitSha: 15c414330343ef77a2c1e86c0f3b1e42d6470ea2
threadCount: 8
---

## Thread 1

- threadId: PRRT_kwDOQ59d5s6Nlc96
- path: packages/shared/src/header/notification-center/normalizeNotificationMessages.ts
- line: 147
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/normalizeNotificationMessages.ts, packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
This is not readable. The ?? should be somewhere else. Not sure what you are checking but it might be in the argument or a previous variable construction.
Also, why we need this default? Add a minimal comment to explain.

**Resolution:**
Valid. Extracted `resolveOneClickFilledBaseAmount` so orderSize vs filledBase precedence lives in one helper with an explicit early return instead of inline `??`.

## Thread 2

- threadId: PRRT_kwDOQ59d5s6NlglU
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 125
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
What do you mean by "wire values"?

**Resolution:**
Valid. Replaced 'wire values' wording with a docstring that names Hermod scaled integers vs Door display-normalized floats.

## Thread 3

- threadId: PRRT_kwDOQ59d5s6NlhV4
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 128
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
Isn't a typing or previous check somewhere (maybe in the socket message) that prevent us from using this broad type?

**Resolution:**
Valid. `rawAmount` is now typed as `ScaledInteger` from `@roxom-markets/schemas`, matching `OrderUpdatePayload`.

## Thread 4

- threadId: PRRT_kwDOQ59d5s6Nlhmo
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 131
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
Never use loose equality

**Resolution:**
Valid. Replaced loose `== null` checks with explicit `=== null` / `=== undefined`.

## Thread 5

- threadId: PRRT_kwDOQ59d5s6Nlik4
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 135
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
I don't want hardcoded magic numbers. I think we have proper constants somewhere else for these defaults, maybe even in the schemas repo.

**Resolution:**
Valid. Cap uses `BTC.PRECISION.BTC`; fallback uses `DEFAULT_DISPLAY_BASE_DECIMALS` (spot display default, aligned with CashInOut).

## Thread 6

- threadId: PRRT_kwDOQ59d5s6NlrSg
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 138
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
What are we trimming if the rawAmount is actually a number and you already checked it with the isScaledIntegerWire method?

**Resolution:**
Valid. `trim()` only runs on string scaled integers; bigint/number paths use `String()` without trimming.

## Thread 7

- threadId: PRRT_kwDOQ59d5s6NltYT
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 203
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
I don't fully understand what this method is about and why we need it. Add the proper docstring if we actually need it explaining the what and why.

**Resolution:**
Valid. Added a docstring on `isScaledIntegerWire` explaining scaled integers vs display floats and why we branch.

## Thread 8

- threadId: PRRT_kwDOQ59d5s6Nl1ra
- path: packages/shared/src/header/notification-center/helpers.ts
- line: 127
- verdict: valid
- reviewer: lucasfvera
- changedFiles: packages/shared/src/header/notification-center/helpers.ts

**Reviewer comment:**
It is confusing to have that many return scattered around. Try to make it so we have a clear path on what we return from this method.

**Resolution:**
Valid. `formatOneClickOrderBaseAmount` now assigns to a single `formatted` variable and returns once at the end.
