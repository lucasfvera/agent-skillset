---
id: 20260704T020406Z-roxom-markets-roxtopia-pr874
status: pending
capturedAt: 2026-07-04T02:04:06Z
actionedAt: null
pr: roxom-markets/roxtopia#874
prUrl: https://github.com/roxom-markets/roxtopia/pull/874
fixCommitSha: cbb84759f
threadCount: 1
---

## Thread 1

- threadId: review:4628667969
- path: —
- line: —
- verdict: valid
- reviewer: lucasfvera
- changedFiles:
  - packages/shared/src/header/notification-center/BellButton.tsx
  - packages/shared/src/header/notification-center/NotificationCenterClient.tsx
  - packages/shared/src/header/notification-center/NotificationItem.tsx

### Reviewer comment

We still have some hardcoded arbitrary values instead of tailwind tokens. I want you to check our existing styles tokens in spark ui and try to find the closest value that would work. For instance, I see text-[13px]; if there is a token that represents + or - 1px, that will be good enough. Same for coloring, opacity, etc; try to find the closest value that is in our design system in spark ui.
The goal is to have the least possible arbitrary values. If you find that some tokens cannot be replaced with existing ones, raise it in a comment and leave it as is.

### Resolution

Valid. I checked the Spark UI Tailwind preset and globals, then replaced the arbitrary values that had exact or close existing tokens: 13px text now uses `text-sm`, matching Spark UI's 13px override; 14/20/24/48/288px dimensions now use spacing tokens; 3px gap, 5/6px dots, line heights, and hardcoded gray/purple values now use existing Tailwind or Spark UI tokens.

I left the remaining arbitrary values where I did not find a close existing token: 10px badge/meta text, the 480px popover cap, the existing custom popover shadow, the 34px bell button, the 18px bell icon, and the `calc()` badge offset.

Block review first found that the 10px label should stay arbitrary because `text-xs` is 12px and outside the requested tolerance. After restoring that value, the second block review passed.
