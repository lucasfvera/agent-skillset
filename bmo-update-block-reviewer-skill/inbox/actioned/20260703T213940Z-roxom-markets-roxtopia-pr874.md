---
id: 20260703T213940Z-roxom-markets-roxtopia-pr874
status: actioned
capturedAt: 2026-07-03T21:39:40Z
actionedAt: 2026-08-06T18:40:26Z
pr: roxom-markets/roxtopia#874
prUrl: https://github.com/roxom-markets/roxtopia/pull/874
fixCommitSha: 73bd551c0
threadCount: 1
---

## Thread 1

- threadId: review:4627987183
- path: —
- line: —
- verdict: valid
- reviewer: dieduro
- changedFiles:
  - packages/shared/src/header/notification-center/BellButton.tsx
  - packages/shared/src/header/notification-center/NotificationCenterClient.tsx
  - packages/shared/src/header/notification-center/NotificationItem.tsx

### Reviewer comment

Dear agent, I see you're using some hardcoded color values. I'd actually like you to check in spark-ui library whether we have a variable for them and if we don't evaluate whether it's worth to create a variant in a component or a token variable for it. We'r trying to avoid arbitrary values in tailwind classes

### Resolution

Valid. I checked the Spark UI Tailwind preset and globals before changing code. Existing tokens cover this case, so I replaced the arbitrary popover/bell color utilities with `action-danger`, `txt-secondary`, `txt-muted`, and `surface-2` instead of adding new tokens or variants.

Block review found no blocking issues before publish.
