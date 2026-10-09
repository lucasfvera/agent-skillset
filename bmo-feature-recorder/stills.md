# Stills (destination `pr` only)

Clip destinations never read this file. Load after the brief exists.

Capture with **`agent-browser`**. `/bmo-pr` uploads; this file stops at PNGs on disk.

## Tooling

```bash
command -v agent-browser >/dev/null 2>&1 && agent-browser --version
```

Exit **0** and a version line required. If missing, **push back** — tell the caller to install, then stop:

```text
npm install -g agent-browser && agent-browser install
```

Do not substitute Cursor browser MCP or Playwright.

**Done:** `agent-browser --version` printed. Otherwise stopped.

## Mode

Already chosen in the brief.

| Mode | What to capture |
|------|-----------------|
| **before/after** | Same URL/path, same viewport: **after** on the PR branch, **before** on base (or a still-base prod/QA URL) |
| **implementation-only** | After shots of the new surface |

If before is blocked (no runnable base, no stable base URL), fall back to **implementation-only** and note it in `take.json`. Do not invent a fake before.

## Sessions

Auth from the brief. Two sessions; leftover cookies do not cross.

| Auth | Session |
|------|---------|
| logged-out | `--session anon` (no state) |
| logged-in | `--session authed` |
| both | both sessions; stills named with `anon-` / `authed-` |

**Logged-in state** (first match):

1. `AGENT_BROWSER_STATE` names an existing file, or a prior `state save` from this run — `agent-browser --session authed --state <file>`
2. `E2E_USER_EMAIL` and `E2E_USER_PASSWORD` are set (Cursor Runtime Secrets). Open the app login origin, fill from those env vars, `state save`, then walk. Never print the values.
3. Else **push back** — logged-in stills need state or secrets.

**Done:** each briefed auth has a session ready, or push back.

## Capture

Base URL from README / `package.json` scripts, or a QA/preview host the caller named. Viewport desktop unless the change is mobile-specific; keep before and after identical.

```bash
OUT="${TMPDIR:-/tmp}/bmo-feature-stills/<slug>"
mkdir -p "$OUT"

agent-browser --session <anon|authed> open "<absolute-url>"
agent-browser wait 2000
# optional: click the briefed control, then wait once more
agent-browser screenshot "$OUT/<name>.png"
```

Settle = **2000 ms** after open (or after the click) unless a known spinner needs one longer wait.

**Names:**

- before/after: `<route-slug>-before.png`, `<route-slug>-after.png`
- implementation-only: `<route-slug>-after.png` (or `-01`, `-02`)
- both auths: prefix `anon-` / `authed-`

**before/after order (local app):**

1. App on the **PR branch** → capture **after**
2. Base (`git checkout origin/<base>` in a worktree, or a still-base remote URL) → same URL → **before** → restore the PR branch

If capture fails (app down, auth wall, bad URL), **push back** and stop.

Write `take.json` in `OUT`: origins (no emails), every briefed surface as true/false, `recordedAt`, `slug`, `mode`.

**Done:** every planned PNG exists and is readable; `take.json` has a true/false field per surface (false allowed; omitting the field is not); branch restored if you checked out base.
