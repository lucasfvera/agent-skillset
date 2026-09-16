---
id: 20260903T185227Z-roxom-markets-roxtopia-pr1179
status: actioned
capturedAt: 2026-09-03T18:52:27Z
actionedAt: 2026-09-16T05:37:22Z
pr: roxom-markets/roxtopia#1179
prUrl: https://github.com/roxom-markets/roxtopia/pull/1179
fixCommitSha: a0bb3c5f6
threadCount: 4
---

## Thread 1

- threadId: PRRT_kwDOQ59d5s6fBPzg
- path: packages/shared/src/kyc/useConfig.ts
- line: 1
- verdict: valid
- reviewer: dieduro
- changedFiles:
  - packages/shared/src/app-config/useConfig.ts
  - packages/shared/src/kyc/useConfig.ts
  - packages/shared/src/providers/feature-flags/index.tsx

**Reviewer comment**

this `useConfig` under kyc does not make sense to me. we might have a duplicated `useConfig` right?

**Resolution**

Valid. I moved the real client config query out of KYC and into `packages/shared/src/app-config/useConfig.ts`, kept `packages/shared/src/kyc/useConfig.ts` as a compatibility re-export, and made `FeatureFlagProvider` consume the same shared hook.

## Thread 2

- threadId: PRRT_kwDOQ59d5s6fCU5Q
- path: packages/shared/src/providers/feature-flags/index.tsx
- line: 20
- verdict: valid
- reviewer: lucasfvera
- changedFiles:
  - packages/shared/src/app-config/useConfig.ts
  - packages/shared/src/kyc/useConfig.ts
  - packages/shared/src/providers/feature-flags/index.tsx

**Reviewer comment**

Why do we use CONFIG_PATH instead of using the Endpoint namespace we have in place and already use everywhere else?

**Resolution**

Valid. Removed the local `CONFIG_PATH` / raw fetch from `FeatureFlagProvider`; the shared config hook now uses `Endpoints.CONFIG.GET` with `cache: "no-store"`, so feature flags and `useConfig` share one fetch path.

## Thread 3

- threadId: review:5105087743
- path: —
- line: —
- verdict: valid
- reviewer: dieduro
- changedFiles:
  - packages/shared/src/app-config/useConfig.ts
  - packages/shared/src/kyc/useConfig.ts
  - packages/shared/src/providers/feature-flags/index.tsx

**Reviewer comment**

minor comment about a possible duplicated hook

**Resolution**

Valid. Covered by the inline fix: the client config hook now lives outside KYC, with the KYC path kept only as a compatibility re-export.

## Thread 4

- threadId: review:5105567544
- path: —
- line: —
- verdict: partially_valid
- reviewer: lucasfvera
- changedFiles:
  - packages/shared/src/app-config/useConfig.ts
  - packages/shared/src/kyc/useConfig.ts
  - packages/shared/src/providers/feature-flags/index.tsx

**Reviewer comment**

I noticed there are other places we call the config endpoint, mostly server side but it might be still something to keep in mind since those fetches would also need the no cache header?

**Resolution**

Partially valid. I kept server-side `/config` fetches unchanged because this PR targets browser HTTP cache on active client refetches; the changed client fetch path is now centralized and uses `cache: "no-store"`.
