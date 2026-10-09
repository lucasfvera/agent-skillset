---
name: bmo-feature-recorder
description: Captures a feature walk as PR stills (agent-browser) or a growth video clip for email and chat.
disable-model-invocation: true
argument-hint: "[feature, or Destination: pr handoff]"
---

# Feature walk

Evidence of one feature walk. **Destination** picks the artifact. Not a review brief (`/bmo-review-report`).

Leave recorders, clips, stills, and `take.json` untracked unless the user asks to commit them.

**Input:** `$ARGUMENTS` is the feature in the user's words, **or** a PR handoff (`Destination: pr` plus slug, surfaces, auth, mode). If neither, ask once, then stop.

## 1. Brief the walk

Write:

- Feature name and a kebab **slug**
- **Destination:** `pr` | `local` | `email` | `message`
  - `pr` when the caller is `/bmo-pr` or the handoff says `Destination: pr`
  - `email` / `message` when the user said email, gift, Slack, or send
  - else `local`
- Ordered **surfaces**: URL (or path), control, expected state after the click or load
- **Auth:** logged-in, logged-out, or both
- **Mode** (destination `pr` only): `before/after` or `implementation-only`

Turn speech or the PR handoff into that list. If they named a PR, issue, or screen, look up the real routes and controls. If a surface is still ambiguous, ask once.

**Done:** slug, destination, auth, and an ordered surface list exist. Every surface has a URL or path and a control. Destination `pr` also has a mode.

## 2. Capture

Read **one** file. Do not load the other branch.

| Destination | Read |
|-------------|------|
| `pr` | [stills.md](stills.md) |
| `local`, `email`, `message` | [`../bmo-review-report/sentiless.md`](../bmo-review-report/sentiless.md), then [record.md](record.md). When writing or adapting a recorder, also read [`../bmo-review-report/cursor-overlay.md`](../bmo-review-report/cursor-overlay.md) before the first `page.mouse` call. |

On **push back**, stop — no fake take.

**Done:** `take.json` lists every briefed surface as true/false, and the destination artifact exists (PNGs under `OUT` for `pr`; `<slug>.webm` for a clip).

## 3. Hand off

| Destination | Action |
|-------------|--------|
| `pr` | Report `OUT` and `take.json` to the caller (chat if this skill was typed by hand). `/bmo-pr` uploads. |
| `local` | Report the absolute webm path in chat. |
| `email` or `message` | Read [share.md](share.md). |

**Done:** the caller has PNG paths (`pr`) or a playable file path (clip; mp4 when email/message).
